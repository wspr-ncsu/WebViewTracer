package flow

import (
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/url"
	"os"
	"regexp"
	"strconv"
	"strings"

	"github.com/lib/pq"
	"github.com/wspr-ncsu/visiblev8/post-processor/core"
)

type JavaExfil struct {
	MockTime uint64
	offset   uint64
	API      string
	exfilUrl *url.URL
}

type JavaArgs struct {
	MockTime uint64
	offset   uint64
	API      string
	Args     string
}

type Script struct {
	APIs               []string
	JavaAPIs           []string
	JavaRetVals        []string
	JavaExfils         []*JavaExfil
	JavaArgs           []string
	structuredJavaArgs []*JavaArgs
	bucketList         []string
	arguments          []string
	info               *core.ScriptInfo
}

func NewScript(info *core.ScriptInfo) *Script {
	return &Script{
		APIs:               make([]string, 0),
		bucketList:         make([]string, 0),
		arguments:          make([]string, 0),
		JavaAPIs:           make([]string, 0),
		JavaRetVals:        make([]string, 0),
		JavaArgs:           make([]string, 0),
		JavaExfils:         make([]*JavaExfil, 0),
		structuredJavaArgs: make([]*JavaArgs, 0),
		info:               info,
	}
}

type APICategories map[string]map[string]map[string]string

type flowAggregator struct {
	scriptList       map[int]*Script
	apiCats          APICategories
	idlTree          core.IDLTree
	lastAction       string
	secondLastMember string
	lastWindowGet    string
	lastMember       string
	urlRegex         regexp.Regexp
	requestRegex     regexp.Regexp
	injectionLookup  map[string]bool
}

func LoadAPICategories(filePath string) (APICategories, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	content, err := io.ReadAll(file)
	if err != nil {
		return nil, err
	}

	var apiCategories APICategories

	err = json.Unmarshal(content, &apiCategories)
	if err != nil {
		return nil, err
	}

	return apiCategories, nil
}

func (agg *flowAggregator) MatchActionToBucket(receiver string, member string, op string, isJava bool) string {
	rules := agg.apiCats

	if op == "c" && isJava {
		return "Java"
	}

	// Check specific receiver first
	if members, exists := rules[receiver]; exists {
		if ops, exists := members[member]; exists {
			if bucket, exists := ops[op]; exists {
				return bucket
			}
			if bucket, exists := ops["*"]; exists {
				return bucket
			}
		}
	}

	// Check wildcard receiver
	if members, exists := rules["*"]; exists {
		if ops, exists := members[member]; exists {
			if bucket, exists := ops[op]; exists {
				return bucket
			}
			if bucket, exists := ops["*"]; exists {
				return bucket
			}
		}
	}

	if agg.idlTree.IsAPIInIDLFile(byte(op[0]), receiver, member) {
		return "notidlapi"
	}

	return "unmatched"
}

func (agg *flowAggregator) NewJavaArgs(mockTime uint64, offset uint64, javaArg string, api string) *JavaArgs {
	return &JavaArgs{
		MockTime: mockTime,
		offset:   offset,
		Args:     javaArg,
		API:      api,
	}
}

func NewAggregator() (core.Aggregator, error) {
	apiBucketsFile := os.Getenv("ANDROID_API_BUCKETS_FILE")
	if apiBucketsFile == "" {
		apiBucketsFile = "./android_apis_buckets.json"
	}
	apiCats, err := LoadAPICategories(apiBucketsFile)
	if err != nil {
		return nil, err
	}

	idlTree, err := core.LoadDefaultIDLData()
	if err != nil {
		return nil, err
	}

	requestPattern := regexp.MustCompile(`(?:request|post|\:\/\/)`)
	// Bastardized URL regex, do not touch this otherwise your research won't finish in this decade
	urlRegex := regexp.MustCompile(`([A-Za-z]{3,9}:\/\/[A-Za-z0-9.-]+(?:\/[\\+~%\/.\w\-_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*)?)`)

	return &flowAggregator{
		scriptList:   make(map[int]*Script),
		apiCats:      apiCats,
		idlTree:      idlTree,
		requestRegex: *requestPattern,
		urlRegex:     *urlRegex,
	}, nil
}

func (agg *flowAggregator) likeExfil(args []string) bool {

	for _, arg := range args {
		if agg.requestRegex.MatchString(arg) {
			return true
		}
	}

	return false
}

func (agg *flowAggregator) NewJavaExfil(mockTime uint64, api string, args []string) (*JavaExfil, error) {
	urlStr := "THISISNOTAVALIDURL"
	var parsedURL *url.URL = nil
	for _, arg := range args {
		// the URL match is expensive so we optimize our complexity by doing a O(n)
		// bad match for a singular string before actually committing to the bit
		//fmt.Printf("Hello %s\n", arg)
		if strings.Contains(arg, "://") {
			if agg.urlRegex.MatchString(arg) {
				matches := agg.urlRegex.FindStringSubmatch(arg)
				urlStr = matches[1]
				//fmt.Printf("-> %s\n", urlStr)
				parsedURL, _ = url.Parse(urlStr)
				if parsedURL != nil {
					break
				}
			}
		}
	}

	//fmt.Printf("New Java Exfil -> %s %t %t", urlStr, parsedURL == nil, urlStr == "THISISNOTAVALIDURL\n")

	if urlStr == "THISISNOTAVALIDURL" || parsedURL == nil {
		return nil, fmt.Errorf("unable to find a url")
	}

	return &JavaExfil{
		MockTime: mockTime,
		API:      api,
		exfilUrl: parsedURL,
	}, nil
}

func (agg *flowAggregator) IngestRecord(ctx *core.ExecutionContext, lineNumber int, op byte, fields []string) error {
	if (ctx.Script != nil) && !ctx.Script.VisibleV8 && (ctx.Origin.Origin != "") {
		offset, err := strconv.Atoi(fields[0])
		if err != nil {
			return fmt.Errorf("%d: invalid script offset '%s'", lineNumber, fields[0])
		}

		script, ok := agg.scriptList[ctx.Script.ID]

		if !ok {
			script = NewScript(ctx.Script)
			agg.scriptList[ctx.Script.ID] = script
		}

		var receiver, member string
		var args []string
		switch op {
		case 'g', 's':
			receiver, _ = core.StripCurlies(fields[1])
			member, _ = core.StripQuotes(fields[2])
			args = fields[3:]
		case 'n':
			receiver, _ = core.StripCurlies(fields[1])
			receiver = strings.TrimPrefix(receiver, "%")
			args = fields[2:]
		case 'c':
			receiver, _ = core.StripCurlies(fields[2])
			member, _ = core.StripQuotes(fields[1])
			args = fields[3:]

			member = strings.TrimPrefix(member, "%")
		case 'j':
			returnVal, _ := core.StripCurlies(fields[4])
			script.JavaRetVals = append(script.JavaRetVals, returnVal)
			return nil
		default:
			return nil //fmt.Errorf("%d: invalid mode '%c'; fields: %v", lineNumber, op, fields)
		}

		var jsonArgs, _ = json.Marshal(args)

		if core.FilterName(member) {
			// We have some names (V8 special cases, numeric indices) that are never useful
			return nil
		}

		if strings.Contains(receiver, ",") {
			receiver = strings.Split(receiver, ",")[1]
		}

		var fullName string
		if member != "" {
			fullName = fmt.Sprintf("%s.%s", receiver, member)
		} else {
			fullName = receiver
		}

		if strings.HasPrefix("Window", fullName) && op == 'g' {
			agg.lastWindowGet = member
		}

		if strings.HasPrefix("Object.<anonymous>", fullName) && len(script.APIs) > 2 {
			script.APIs = script.APIs[:len(script.APIs)-1]
			script.APIs = append(script.APIs, fmt.Sprintf("%d,%d,%s.%s,c,Java", ctx.MockTime, offset, agg.lastWindowGet, agg.lastMember))
			script.bucketList = script.bucketList[:len(script.bucketList)-1]
			script.arguments = script.arguments[:len(script.arguments)-1]
			script.bucketList = append(script.bucketList, agg.MatchActionToBucket(agg.secondLastMember, agg.lastMember, "c", true))
			script.arguments = append(script.arguments, string(jsonArgs))
			script.JavaAPIs = append(script.JavaAPIs, fmt.Sprintf("%s.%s", agg.lastWindowGet, agg.lastMember))
			script.JavaArgs = append(script.JavaArgs, string(jsonArgs))
			script.structuredJavaArgs = append(script.structuredJavaArgs, agg.NewJavaArgs(ctx.MockTime, uint64(offset), string(jsonArgs), fmt.Sprintf("%s.%s", agg.lastWindowGet, agg.lastMember)))
			if agg.likeExfil(args) {
				javaExfil, err := agg.NewJavaExfil(ctx.MockTime, fmt.Sprintf("%s.%s", agg.lastWindowGet, agg.lastMember), args)
				if err != nil {
					// oops we identified the wrong thing?
				} else {
					script.JavaExfils = append(script.JavaExfils, javaExfil)
				}
			}
			agg.lastAction = fmt.Sprintf("%d,%s.%s,c", offset, agg.secondLastMember, agg.lastMember)
			return nil
		}

		currentAction := fmt.Sprint(offset) + string(',') + fullName
		currentAPI := fmt.Sprintf("%d,%s,%s", ctx.MockTime, currentAction, string(op))

		if agg.lastAction == currentAction && op == 'c' && len(script.APIs) > 0 && script.APIs[len(script.APIs)-1] == currentAction+string(',')+string(op) {
			script.APIs = script.APIs[:len(script.APIs)-1]
			script.APIs = append(script.APIs, currentAPI)
			script.bucketList = script.bucketList[:len(script.bucketList)-1]
			script.arguments = script.arguments[:len(script.arguments)-1]
			script.bucketList = append(script.bucketList, agg.MatchActionToBucket(receiver, member, string(op), false))
			script.arguments = append(script.arguments, string(jsonArgs))
			agg.lastAction = currentAction
			return nil
		}

		script.APIs = append(script.APIs, currentAPI)
		script.bucketList = append(script.bucketList, agg.MatchActionToBucket(receiver, member, string(op), false))
		script.arguments = append(script.arguments, string(jsonArgs))
		agg.secondLastMember = agg.lastMember
		agg.lastMember = member
		agg.lastAction = currentAction
	}

	return nil
}

var scriptFlowFields = [...]string{
	"identif",
	"isolate",
	"mock_time",
	"visiblev8",
	"code",
	"url",
	"evaled_by_uuid",
	"apis",
	"java_apis",
	"java_args",
	"java_ret_val",
	"bucket_list",
	"arguments",
	"sha256",
	"first_origin",
	"log_id",
	"package_name",
	"is_injection",
}

var javaExfilFields = [...]string{
	"identif",
	"mock_time",
	"apioffset",
	"evaled_by_uuid",
	"log_id",
	"sha256",
	"api",
	"url_host",
	"url_protocol",
	"url_query",
	"url_path",
}

var javaArgsFields = [...]string{
	"identif",
	"mock_time",
	"apioffset",
	"evaled_by_uuid",
	"log_id",
	"sha256",
	"api",
	"java_arg",
}

func (agg *flowAggregator) CheckIfInjectionBulk(scripts []*Script, sqlDb *sql.DB) map[string]bool {
	results := make(map[string]bool)
	if len(scripts) == 0 {
		return results
	}

	// Prepare a slice of hashes and a map for tracking results
	var hashes [][]byte
	hashToScript := make(map[string]bool)

	for _, script := range scripts {
		hash := script.info.CodeHash.SHA2[:]
		hashes = append(hashes, hash)
		hashToScript[hex.EncodeToString(hash)] = false // Default to false
	}

	// Query the database for matching hashes
	query := `SELECT sha256 FROM injection_log WHERE sha256 = ANY($1)`
	rows, err := sqlDb.Query(query, pq.Array(hashes))
	if err != nil {
		return results
	}
	defer rows.Close()

	// Mark found hashes as true
	for rows.Next() {
		var sha256 []byte
		if err := rows.Scan(&sha256); err == nil {
			hashToScript[hex.EncodeToString(sha256)] = true
		}
	}

	// fmt.Printf("Sanity check, we reach this point")

	return hashToScript
}

func (agg *flowAggregator) CheckIfInjection(script *Script) bool {

	// fmt.Printf("---------------------- BUCKLE UP -----------------------\n")
	// for k, v := range agg.injectionLookup {

	// 	fmt.Println(k, "value is", v)
	// }
	// fmt.Printf("The hash you are searching for is %s\n", hex.EncodeToString(script.info.CodeHash.SHA2[:]))
	// fmt.Printf("----------------------- BUCKLE DOWN ---------------------\n")

	is_injection, ok := agg.injectionLookup[hex.EncodeToString(script.info.CodeHash.SHA2[:])]
	if !ok {
		fmt.Println("@@@We should not be here@@@")
	}
	return is_injection
}

func (agg *flowAggregator) DumpNormalFlowToPostgresql(ctx *core.AggregationContext, sqlDb *sql.DB, logId int) error {
	txn, err := sqlDb.Begin()
	if err != nil {
		return err
	}

	stmt, err := txn.Prepare(pq.CopyIn("script_flow", scriptFlowFields[:]...))
	if err != nil {
		txn.Rollback()
		return err
	}

	log.Printf("scriptFlow: %d scripts analysed", len(agg.scriptList))

	for _, script := range agg.scriptList {
		evaledBy := script.info.EvaledBy

		var evaledByUUID = ""

		if evaledBy != nil {
			evaledByUUID = evaledBy.UniqueIdentifier.String()
		}

		_, err = stmt.Exec(
			script.info.UniqueIdentifier.String(),
			script.info.Isolate.ID,
			script.info.MockTime,
			script.info.VisibleV8,
			script.info.Code,
			script.info.URL,
			evaledByUUID,
			pq.Array(script.APIs),
			pq.Array(script.JavaAPIs),
			pq.Array(script.JavaArgs),
			pq.Array(script.JavaRetVals),
			pq.Array(script.bucketList),
			pq.Array(script.arguments),
			script.info.CodeHash.SHA2[:],
			script.info.FirstOrigin.Origin,
			logId,
			ctx.PackageName,
			agg.CheckIfInjection(script),
		)

		if err != nil {
			txn.Rollback()
			return err
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

func (agg *flowAggregator) DumpJavaExfilToPostgresql(ctx *core.AggregationContext, sqlDb *sql.DB, logId int) error {
	txn, err := sqlDb.Begin()
	if err != nil {
		return err
	}

	stmt, err := txn.Prepare(pq.CopyIn("java_exfil", javaExfilFields[:]...))
	if err != nil {
		txn.Rollback()
		return err
	}

	log.Printf("scriptFlow: %d scripts analysed for Java exfil", len(agg.scriptList))

	for _, script := range agg.scriptList {

		evaledBy := script.info.EvaledBy

		var evaledByUUID = ""

		if evaledBy != nil {
			evaledByUUID = evaledBy.UniqueIdentifier.String()
		}

		for _, javaExfil := range script.JavaExfils {
			_, err = stmt.Exec(
				script.info.UniqueIdentifier,
				javaExfil.MockTime,
				javaExfil.offset,
				evaledByUUID,
				logId,
				script.info.CodeHash.SHA2[:],
				javaExfil.API,
				javaExfil.exfilUrl.Hostname(),
				javaExfil.exfilUrl.Scheme,
				javaExfil.exfilUrl.RawQuery,
				javaExfil.exfilUrl.Path,
			)

			if err != nil {
				txn.Rollback()
				return err
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

func (agg *flowAggregator) DumpJavaArgsToPostgresql(ctx *core.AggregationContext, sqlDb *sql.DB, logId int) error {
	txn, err := sqlDb.Begin()
	if err != nil {
		return err
	}

	stmt, err := txn.Prepare(pq.CopyIn("java_args", javaArgsFields[:]...))
	if err != nil {
		txn.Rollback()
		return err
	}

	log.Printf("scriptFlow: %d scripts analysed for Java exfil", len(agg.scriptList))

	for _, script := range agg.scriptList {

		evaledBy := script.info.EvaledBy

		var evaledByUUID = ""

		if evaledBy != nil {
			evaledByUUID = evaledBy.UniqueIdentifier.String()
		}

		for _, javaArgs := range script.structuredJavaArgs {
			_, err = stmt.Exec(
				script.info.UniqueIdentifier,
				javaArgs.MockTime,
				javaArgs.offset,
				evaledByUUID,
				logId,
				script.info.CodeHash.SHA2[:],
				javaArgs.API,
				javaArgs.Args,
			)

			if err != nil {
				txn.Rollback()
				return err
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

func (agg *flowAggregator) DumpToPostgresql(ctx *core.AggregationContext, sqlDb *sql.DB) error {

	logId, err := ctx.Ln.InsertLogfile(sqlDb)

	if err != nil {
		return err
	}

	var scripts []*Script
	for _, script := range agg.scriptList {
		scripts = append(scripts, script)
	}

	agg.injectionLookup = agg.CheckIfInjectionBulk(scripts, sqlDb)

	err = agg.DumpNormalFlowToPostgresql(ctx, sqlDb, logId)

	if err != nil {
		return err
	}

	err = agg.DumpJavaExfilToPostgresql(ctx, sqlDb, logId)

	if err != nil {
		return err
	}

	return nil
}

func (agg *flowAggregator) DumpToStream(ctx *core.AggregationContext, stream io.Writer) error {
	jstream := json.NewEncoder(stream)

	for _, script := range agg.scriptList {
		evaledBy := script.info.EvaledBy

		evaledById := -1
		if evaledBy != nil {
			evaledById = evaledBy.ID
		}

		jstream.Encode(core.JSONArray{"script_flow", core.JSONObject{
			"ID":          script.info.ID,
			"Isolate":     script.info.Isolate.ID,
			"IsVisibleV8": script.info.VisibleV8,
			"Code":        script.info.Code,
			"URL":         script.info.URL,
			"IsEvaledBy":  evaledById,
			"FirstOrigin": script.info.FirstOrigin,
			"APIs":        script.APIs,
			"BucketList":  script.bucketList,
			"Arguments":   script.arguments,
			"SHA256":      core.NewScriptHash(script.info.Code).SHA2,
		}})
	}

	return nil
}
