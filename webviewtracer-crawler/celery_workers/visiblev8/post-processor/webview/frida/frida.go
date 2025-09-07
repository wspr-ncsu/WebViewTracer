package main

import (
	"bufio"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"

	"github.com/lib/pq"
	_ "github.com/lib/pq"
	"github.com/vincent-petithory/dataurl"
	"github.com/wspr-ncsu/visiblev8/post-processor/core"
)

type DataField struct {
	Action   *string   `json:"action,omitempty"`   // Optional field.
	Hashcode *int64    `json:"hashcode,omitempty"` // Optional field.
	Func     *string   `json:"func,omitempty"`     // Optional field.
	Params   *[]string `json:"params,omitempty"`   // Optional field.
}

type Record struct {
	Data       *DataField `json:"data,omitempty"`
	Stacktrace string     `json:"stacktrace,omitempty"`
	Type       string     `json:"type,omitempty"`
	Hashcode   int64      `json:"hashcode,omitempty"`
	ClassName  string     `json:"className,omitempty"`
}

// TODO: adjust based on actual file path
func getAppName(filename string) string {
	paths := strings.Split(filename, "/")
	return paths[len(paths)-4]
}

func VisitFile(fp string, fi os.FileInfo, err error) error {
	db := "vv8_backend"

	if err != nil {
		fmt.Println(err) // can't walk here,
		return nil       // but continue walking elsewhere
	}
	if !fi.Mode().IsRegular() {
		return nil // ignore non-files, for instance, directories
	}

	match, err := filepath.Match("webview*.txt", fi.Name())
	if err != nil {
		fmt.Println(err)
		return err
	}

	if match {
		fmt.Println(fp) // print full file path
		parse(fp, db)
	}
	return nil
}

func isInjection(action string, func_name string) (bool, int8, int8) {
	if !strings.Contains(action, "INJECT") {
		return false, -1, -1
	}

	if func_name == "evaluateJavascript" {
		return true, 0, -1
	} else if func_name == "loadData" {
		return true, 0, -1
	} else if func_name == "loadDataWithBaseURL" {
		return true, 1, 0
	} else if func_name == "loadUrlWithHeaders" {
		return true, -1, 0
	} else if func_name == "loadUrl" {
		return true, -1, 0
	} else {
		return false, -1, -1
	}
}

func loadThirdPartyLibraryNames() []string {
	third_party_library_names := []string{}
	file, err := os.Open(os.Getenv("THIRD_PARTY_LIBRARY_NAMES_FILE"))
	if err != nil {
		log.Fatalf("failed to 3p library names file: %s", err)
	}

	scanner := bufio.NewScanner(file)
	scanner.Split(bufio.ScanLines)

	for scanner.Scan() {
		line := scanner.Text()
		third_party_library_names = append(third_party_library_names, line)
	}

	file.Close()

	return third_party_library_names
}

func IsHTMLSpoof(action string, func_name string) bool {
	if func_name == "loadData" {
		return true
	} else if func_name == "loadDataWithBaseURL" {
		return true
	} else {
		return false
	}
}

func IsLoadURLLeakage(action string, func_name string) bool {
	if func_name == "loadUrl" {
		return true
	} else {
		return false
	}
}

func parse(filename, dbname string) {
	appName := getAppName(filename)
	file, err := os.Open(filename)
	if err != nil {
		log.Fatalf("failed to open file: %s", err)
	}

	third_party_library_name := loadThirdPartyLibraryNames()

	scanner := bufio.NewScanner(file)
	scanner.Split(bufio.ScanLines)
	buf := make([]byte, 0, 2048*2048)
	scanner.Buffer(buf, 2048*2048)

	//connStr := "user=vv8 password=vv8 dbname=" + dbname + " sslmode=disable"
	db, err := sql.Open("postgres", "sslmode=disable")
	if err != nil {
		log.Fatal(err)
	}

	defer db.Close()

	sqlStatement := `INSERT INTO frida_log 
	(app_name, action, js_object_id, java_func, parameters, thirdparty_library, stacktrace, is_3p) 
	VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`

	injectionStatement := `INSERT INTO injection_log 
	(app_name, function_name, url, source_code, sha256, thirdparty_library, ishtmlspoofing, isloadURLLeakage, is_3p)
	VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`

	for scanner.Scan() {
		line := scanner.Text()
		var record Record
		if err := json.Unmarshal([]byte(line), &record); err != nil {
			fmt.Printf("Error parsing JSON: %v\n", err)
			continue
		}

		if record.Stacktrace == "" {
			continue
		}

		thirdp_library := []string{}

		for _, library := range third_party_library_name {
			if strings.Contains(record.Stacktrace, library) {
				thirdp_library = append(thirdp_library, library)
			}
		}

		injection, index, urlIndex := isInjection(*record.Data.Action, *record.Data.Func)
		if injection {
			var args []string = *record.Data.Params
			var url = ""
			if urlIndex != -1 {
				url = args[urlIndex]
			}

			var sourceCode = ""
			if index == -1 {
				sourceCode = args[urlIndex]
			} else {
				sourceCode = args[index]
			}

			var unwrappedSourceCode string
			var unwrappedUrl string

			err = json.Unmarshal([]byte(sourceCode), &unwrappedSourceCode)
			if err != nil {
				unwrappedSourceCode = sourceCode
			}
			json.Unmarshal([]byte(url), &unwrappedUrl)
			if err != nil {
				unwrappedUrl = url
			}

			IsHTMLSpoofing := false

			if IsHTMLSpoof(*record.Data.Action, *record.Data.Func) {
				dataURLHTMLData, err := dataurl.DecodeString(unwrappedSourceCode)
				if err == nil && strings.Contains(dataURLHTMLData.MediaType.ContentType(), "html") {
					unwrappedSourceCode = string(dataURLHTMLData.Data)
				}
				IsHTMLSpoofing = true
			}

			if strings.HasPrefix(*record.Data.Func, "load") {
				// Only loadStuff with a JavaScript URI are injection
				var scriptHash core.ScriptHash = core.NewScriptHash(unwrappedSourceCode)

				db.Exec(
					injectionStatement,
					appName,
					record.Data.Func,
					unwrappedUrl,
					unwrappedSourceCode,
					scriptHash.SHA2[:],
					pq.Array(thirdp_library),
					IsHTMLSpoofing,
					IsLoadURLLeakage(*record.Data.Action, *record.Data.Func),
					len(thirdp_library) != 0,
				)
			} else {
				var scriptHash core.ScriptHash = core.NewScriptHash(unwrappedSourceCode)
				db.Exec(
					injectionStatement,
					appName,
					record.Data.Func,
					unwrappedUrl,
					unwrappedSourceCode,
					scriptHash.SHA2[:],
					pq.Array(thirdp_library),
					IsHTMLSpoofing,
					IsLoadURLLeakage(*record.Data.Action, *record.Data.Func),
					len(thirdp_library) != 0,
				)
			}
		}

		db.Exec(sqlStatement,
			appName,
			record.Data.Action,
			record.Data.Hashcode,
			record.Data.Func,
			pq.Array(record.Data.Params),
			pq.Array(thirdp_library),
			record.Stacktrace,
			len(thirdp_library) != 0,
		)
	}

	file.Close()
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("No arguments provided")
		return
	}
	path := os.Args[1]
	err := filepath.Walk(path, VisitFile)

	if err != nil {
		fmt.Printf("error walking the path %v: %v\n", path, err)
	}

}
