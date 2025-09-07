package exfil

import (
	"bufio"
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/url"
	"os"
	"strconv"
	"strings"

	"github.com/lib/pq"
	"github.com/wspr-ncsu/visiblev8/post-processor/core"
)

type ExfilData struct {
	mode     string
	mockTime uint64
	URL      string
	API      string
	Data     string
}

type Script struct {
	ExfilDataList []*ExfilData
	PostData      string
	info          *core.ScriptInfo
	APIs          []string
}

func NewScript(info *core.ScriptInfo) *Script {
	return &Script{
		ExfilDataList: make([]*ExfilData, 0),
		info:          info,
		APIs:          make([]string, 0),
	}
}

func NewExfilData(mode string, mockTime uint64, URL string, Data string, api string) *ExfilData {
	return &ExfilData{
		mode:     mode,
		mockTime: mockTime,
		URL:      URL,
		API:      api,
		Data:     Data,
	}
}

type exfilAggregator struct {
	scriptList map[int]*Script
	idlTree    core.IDLTree
	exfilAPIs  []string
}

func loadInterestingAPIs() ([]string, error) {
	filename := os.Getenv("EXFIL_API_FILE")
	if filename == "" {
		return nil, fmt.Errorf("environment variable EXFIL_API_FILE is not set")
	}

	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var lines []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		lines = append(lines, scanner.Text())
	}

	if err := scanner.Err(); err != nil {
		return nil, err
	}

	return lines, nil
}

func NewAggregator() (core.Aggregator, error) {
	exfilApis, err := loadInterestingAPIs()
	if err != nil {
		return nil, err
	}

	idlTree, err := core.LoadDefaultIDLData()
	if err != nil {
		return nil, err
	}

	return &exfilAggregator{
		scriptList: make(map[int]*Script),
		exfilAPIs:  exfilApis,
		idlTree:    idlTree,
	}, nil
}

func (agg *exfilAggregator) IngestRecord(ctx *core.ExecutionContext, lineNumber int, op byte, fields []string) error {
	if (ctx.Script != nil) && !ctx.Script.VisibleV8 {
		// Magic incantation that makes Mfeatures not fail on atleast 1 app
		// panic: runtime error: index out of range [2] with length 2 for a get/set directive
		_, err := strconv.Atoi(fields[0])
		if err != nil {
			return fmt.Errorf("%d: invalid script offset '%s'", lineNumber, fields[0])
		}
		var receiver, member string
		var parameters []string
		switch op {
		case 'g', 's':
			receiver, _ = core.StripCurlies(fields[1])
			member, _ = core.StripQuotes(fields[2])
			parameters = fields[3:]
		case 'n':
			receiver, _ = core.StripCurlies(fields[1])
			receiver = strings.TrimPrefix(receiver, "%")
			parameters = fields[2:]
		case 'c':
			receiver, _ = core.StripCurlies(fields[2])
			member, _ = core.StripQuotes(fields[1])
			parameters = fields[3:]

			member = strings.TrimPrefix(member, "%")
		default:
			return nil //fmt.Errorf("%d: invalid mode '%c'; fields: %v", lineNumber, op, fields)
		}

		if core.FilterName(member) {
			// We have some names (V8 special cases, numeric indices) that are never useful
			return nil
		}

		if strings.Contains(receiver, ",") {
			receiver = strings.Split(receiver, ",")[1]
		}

		fullName, err := agg.idlTree.NormalizeMember(receiver, member)
		if err != nil {
			if member != "" {
				fullName = fmt.Sprintf("%s.%s", receiver, member)
			} else {
				fullName = receiver
			}
		}

		script, ok := agg.scriptList[ctx.Script.ID]

		if !ok {
			script = NewScript(ctx.Script)
			agg.scriptList[ctx.Script.ID] = script
		}

		for _, exfilAPI := range agg.exfilAPIs {
			action := fullName + string(',') + string(op)
			if strings.HasPrefix(exfilAPI, action) {
				exfilURLParamNum, err := strconv.Atoi(strings.Split(exfilAPI, ",")[2])
				if err != nil {
					return fmt.Errorf("invalid exfil API '%s'", exfilAPI)
				}
				exfilDataParamNum, err := strconv.Atoi(strings.Split(exfilAPI, ",")[3])
				if err != nil {
					return fmt.Errorf("invalid exfil API '%s'", exfilAPI)
				}

				if exfilURLParamNum == -1 {
					if exfilDataParamNum >= len(parameters) {
						// There is nothing here
						continue
					}
					script.ExfilDataList = append(script.ExfilDataList, NewExfilData("data", ctx.MockTime, "", parameters[exfilDataParamNum], fullName))
				} else if exfilDataParamNum == -1 {
					var urlString string
					err := json.Unmarshal([]byte(parameters[exfilURLParamNum]), &urlString)
					if err != nil {
						fmt.Printf("Error parsing JSON: %v", err)
					}
					script.ExfilDataList = append(script.ExfilDataList, NewExfilData("url", ctx.MockTime, urlString, "", fullName))
				} else {
					if exfilDataParamNum >= len(parameters) || exfilURLParamNum >= len(parameters) {
						// Navigator.sendBeacon,*,0,1
						// We live in truly extraordinary circumstances, comrade. I shall not advance further,
						// lest we trigger a full-scale panic. Holding the line here ensures we live to fight another day,
						// even if our data are unbalanced whereas crashing might cause total annihilation. -- Sodium

						continue
					}
					var urlString string
					err := json.Unmarshal([]byte(parameters[exfilURLParamNum]), &urlString)
					if err != nil {
						fmt.Printf("Error parsing JSON: %v", err)
					}
					var data string
					if exfilDataParamNum >= len(parameters) {
						data = ""
					} else {
						data = parameters[exfilDataParamNum]
					}
					script.ExfilDataList = append(script.ExfilDataList, NewExfilData("data+url", ctx.MockTime, urlString, data, fullName))
				}

				return nil
			}
		}

	}

	return nil
}

var scriptExfilFields = [...]string{
	"identif",
	"isolate",
	"log_id",
	"type",
	"mock_time",
	"script_url",
	"evaled_by_uuid",
	"url_hostname",
	"url_port",
	"url_path",
	"url_query",
	"payload",
	"script_hash",
	"url_protocol",
	"first_origin",
	"package_name",
	"api",
}

func (agg *exfilAggregator) DumpToPostgresql(ctx *core.AggregationContext, sqlDb *sql.DB) error {
	txn, err := sqlDb.Begin()
	if err != nil {
		return err
	}
	stmt, err := txn.Prepare(pq.CopyIn("exfil", scriptExfilFields[:]...))
	if err != nil {
		txn.Rollback()
		return err
	}

	logId, err := ctx.Ln.InsertLogfile(sqlDb)

	if err != nil {
		log.Fatalf("We are screwed, logfiles are not getting inserted for some reason")
	}

	for _, script := range agg.scriptList {
		if len(script.ExfilDataList) > 0 {
			for _, exfilData := range script.ExfilDataList {
				fmt.Printf("%d exfil URLs found\n", len(script.ExfilDataList))

				evaledBy := script.info.EvaledBy

				var evaledByUUID = ""

				if evaledBy != nil {
					evaledByUUID = evaledBy.UniqueIdentifier.String()
				}

				if exfilData.mode == "url" {
					parsedURL, err := url.Parse(exfilData.URL)

					if err != nil {
						fmt.Printf("-> exfilurls: could not parse %s\n", exfilData.URL)
						continue
					}

					if parsedURL.Hostname() == "" {
						parsedOrigin, err := url.Parse(script.info.FirstOrigin.Origin)
						if err != nil {
							fmt.Printf("    %s (error: %v)\n", script.info.FirstOrigin.Origin, err)
						}
						parsedURL.Host = parsedOrigin.Host
						parsedURL.Scheme = parsedOrigin.Scheme
					}

					_, err = stmt.Exec(
						script.info.UniqueIdentifier.String(),
						script.info.Isolate.ID,
						logId,
						exfilData.mode,
						exfilData.mockTime,
						script.info.URL,
						evaledByUUID,
						parsedURL.Hostname(),
						parsedURL.Port(),
						parsedURL.Path,
						parsedURL.RawQuery,
						"",
						script.info.CodeHash.SHA2[:],
						parsedURL.Scheme,
						script.info.FirstOrigin.Origin,
						ctx.PackageName,
						exfilData.API,
					)
					if err != nil {
						txn.Rollback()
						return err
					}
				} else if exfilData.mode == "data" {

					_, err = stmt.Exec(
						script.info.UniqueIdentifier.String(),
						script.info.Isolate.ID,
						logId,
						exfilData.mode,
						exfilData.mockTime,
						script.info.URL,
						evaledByUUID,
						"",
						"",
						"",
						"",
						exfilData.Data,
						script.info.CodeHash.SHA2[:],
						"",
						script.info.FirstOrigin.Origin,
						ctx.PackageName,
						exfilData.API,
					)
					if err != nil {
						txn.Rollback()
						return err
					}
				} else {
					parsedURL, err := url.Parse(exfilData.URL)

					if err != nil {
						fmt.Printf("-> exfilurls: could not parse %s\n", exfilData.URL)
						continue
					}

					if parsedURL.Hostname() == "" {
						parsedOrigin, err := url.Parse(script.info.FirstOrigin.Origin)
						if err != nil {
							fmt.Printf("    %s (error: %v)\n", script.info.FirstOrigin.Origin, err)
						}
						parsedURL.Host = parsedOrigin.Host
						parsedURL.Scheme = parsedOrigin.Scheme
					}

					_, err = stmt.Exec(
						script.info.UniqueIdentifier.String(),
						script.info.Isolate.ID,
						logId,
						exfilData.mode,
						exfilData.mockTime,
						script.info.URL,
						evaledByUUID,
						parsedURL.Hostname(),
						parsedURL.Port(),
						parsedURL.Path,
						parsedURL.RawQuery,
						exfilData.Data,
						script.info.CodeHash.SHA2[:],
						parsedURL.Scheme,
						script.info.FirstOrigin.Origin,
						ctx.PackageName,
						exfilData.API,
					)
					if err != nil {
						txn.Rollback()
						return err
					}
				}
			}
		}
	}

	err = stmt.Close()
	if err != nil {
		txn.Rollback()
		return err
	}
	err = txn.Commit()
	if err != nil {
		return err
	}

	return nil
}

func (agg *exfilAggregator) DumpToStream(ctx *core.AggregationContext, stream io.Writer) error {
	// -----------------------------------------------------------------------------------------
	// TODO: Write this properly at some point when I'm not a few weeks across a deadline
	// -----------------------------------------------------------------------------------------
	// for _, script := range agg.scriptList {
	// 	if len(script.ExfilDataList) > 0 {
	// 		fmt.Fprintf(stream, "Script: %s\n", script.info.URL)
	// 		fmt.Fprintf(stream, "  Exfil URLs:\n")
	// 		for _, exfilUrl := range script.URLs {
	// 			var urlString string

	// 			// Unmarshal the JSON string into the Go string variable
	// 			err := json.Unmarshal([]byte(exfilUrl), &urlString)
	// 			if err != nil {
	// 				log.Fatalf("Error parsing JSON: %v", err)
	// 			}

	// 			// Parse the URL string into a URL object
	// 			parsedURL, err := url.Parse(urlString)
	// 			// parsedURL, err := url.Parse(api)
	// 			if err != nil {
	// 				fmt.Fprintf(stream, "    %s (error: %v)\n", exfilUrl, err)
	// 				os.Exit(-1)
	// 			}
	// 			fmt.Fprintf(stream, "    %s\n", parsedURL.String())
	// 		}
	// 	}
	// }

	return nil
}
