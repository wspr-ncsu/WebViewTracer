# VV8 Post Processor

> **Note** This is fork of the post-processor repo located at the [visiblev8](https://github.com/wspr-ncsu/visiblev8)

Swiss-Army dumping ground of logic related to VisibleV8 (VV8) trace log processing.
Originally tightly integrated to a single workflow (i.e., many assumptions/dependencies w.r.t. databases and filenames); slowly being transmogrified into a standalone, modular toolkit.

## Building

To build the vv8-postprocessors, you need to have the following programs/languages installed:

* `python3` (Preferably > 3.8)
* `Rust` (The project was tested using the 2021 edition)
* `Go` (Any version > 1.13 should be sufficient to build vv8-postprocessors)
* `make`

Once the programs are installed you can build the postprocessors by using the `make` command. A resulting `artifacts/` folder is created which contains all the necessary binaries for running the postprocessors.

## Quick Start

Assuming you have some VV8 log (e.g., `vv8-*.[0-9].log`) files in `$PWD`, you can quickly experiment with the supported modes/tools by letting the output go to `stdout` only (the default) and specifying a single "aggregator" (i.e., output mode) at a time.  E.g., to get a quick summary of features used by execution-context-origin-URL, you can do (note that this is an operation that relies on `idldata.json` being in `$PWD`, too):

```$ ./vv8-post-processor -aggs ufeatures vv8*.log```

The output is a single JSON object containing all browser API features accessed globally (an array of strings under the `allFeatures` key) and an array of per-distinct-origin-URL feature arrays (the `featureOrigins` key).

You can combined multiple aggregation passes in a single run by specifying a `+` delimited list of aggregator names as the argument to the `-aggs` flag when you run the post-processor.  (This approach typically makes sense more in a batch processing situation where outputs are being sent to databases.)

## Input

Log file input can be read from named log files or from `stdin` (by specifying `-` as a filename).
Filenames prefixed by the `@` character are interpreted as MongoDB OIDs from our original MongoDB storage scheme; these require MongoDB credentials to be provided via environment variables;

## Output Modes

By default, output goes to `stdout` (typically in some form of JSON, though each aggregator is free to use a different format).

The original workflow for which `vv8-post-processor` was written involved both MongoDB and PostgreSQL databases used in concert (for live collection of bulk data and for offline aggregation and analysis, respectively).  Hence, most aggregators support `mongo` (MongoDB I/O required) and/or `mongresql` (both MongoDB and PostgreSQL I/O required).  We do not document the particulars here, as we consider these modes to be deprecated for future development.  The source code (including a SQL DDL schema file for PostgreSQL) can provide details for the stubbornly intrepid.

That said, a subsequent PostgreSQL-based workflow (via the `Mfeatures` aggregator; see the `mega` folder for schema details) has proved useful and fairly scalable, so you might want to check that out.

## Other options

* `-submissionid`: Specify the submission ID to which the logs are linked to
* `-log-root`: a way to manually specify a base name for a log file when streaming data from `stdin`

## What are all these aggregators?

* `call_args` **(broken)**: A aggregator that records every call being made and the associated arguments
* `poly_features/features`/`scripts`/`blobs`: 4 different output modes for a single input-processing pass (the original one, actually) that extracts polymorphic and monomorphic feature sites (locations within scripts that used a given feature and how many times; polymorphic and monomorphic instances kept separate), loaded script hashes and metadata (i.e.,  URL or eval-parent hash), and the full binary dump of loaded scripts
* `create_element`: emits records of each call to `Document.createElement`, its script context/location, and its first argument (i.e., what kind of element was being created)
* `causality`/`causality_graphml`: 2 different output modes for a single input-processing pass that uses a bunch of heuristics to try to reconstruct script provenance (what script loaded what other script); the later mode emits GraphML (i.e., XML)
* `ufeatures`: a nice summary of features-touched globally on a per logfile basis
* `androidflow` - This postprocessor takes the log and creates a single table correlating scripts to a sequence of executed APIs alongside a annotation of what kind of API it is (using `./celery_workers/visiblev8/post-processor/android_apis_buckets.json` as a guide). The postprocessor is based on the one proposed by Su et al.[^1] for VV8, used for detecting fingerprinting scripts. In addition to this, `androidflow` also has two more tables, a Java exfil table where it searches for Java interfaces with 'GET', 'POST' or 'REQUEST' in it's arguments and tries to strip out the URL to which the data is being sent to from the arguments and a JavaArgs table which logs the return value and arguments of all Java calls made during the execution of the functions.
* `exfil` - The exfil postprocessor uses the `./celery_workers/visiblev8/post-processor/exfil_apis` file that contains a much more fine grained annotation of the exfiltration APIs mention in the `android_apis_bucket.json` to identify exfiltration APIs and extract the URL and payload, postprocess it and dump it to a table where it can be later queried.
* `frida` - This postprocessor creates two tables, a injection_log and frida_log, frida_log contains a log of all interactions Java code has with WebViews, the injection_log table only contains injections as defined by paper. It also uses `./celery_workers/Third-Party-Library-Names` to resolve the third-party libraries in the stack trace.
* `Mfeatures`: the latest and probably best/richest aggregation of data into a fairly normalized entity-relationship schema of script/instance/feature/usage; requires PostgreSQL (see `mega/postgres_schema.sql`)
* `adblock`: A aggregator which logs which url and origin combinations are blocked by easyprivacy.txt and easylist.txt. We use a the brave adblock engine implementation in Rust.

> **Note**
> To use the `adblock` postprocessor you need to have the `adblock` binary and the easyprivacy.txt and easylist.txt files in the current working directory or set the following variables to the path of thier respective locations.
>
> * `ADBLOCK_BINARY`
> * `EASYLIST_FILE`
> * `EASYPRIVACY_FILE`

* `fptp`: This postprocessor logs each and every script and whether or not they are a third party compared to:
  * The origin in which they were loaded
  * If available via the `submission id`, the root domain in which they were loaded

> [!NOTE]
> To use the `fptp` postprocessor you need to have the `entities.json` file (generated as part of the build process on the VisibleV8 repo) in the current working directory or set the `EMAP_FILE` variable to the path of the file. The generation of the file has been removed from this checkout to allow for faster build times.
