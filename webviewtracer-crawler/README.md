# WebViewTracer Crawler

The WebViewTracer Crawler is a framework which makes large scale crawling of apps with VisibleV8WebView much easier. The WebViewTracer system consists of two major components:
* the VisibleV8Webview, a browser instrumentation framework integrated into WebViews that logs all JavaScript code being executed inside webviews
* the crawler architecture (this one) consisting of the Frida instrumentation (located in `./celery_workers/vv8_worker/uiharvester/frida-scripts/identify_webviews.js`), the overall URLHarvester code (at `./celery_workers/vv8_worker/uiharvester`) and the log postprocessors (at `./celery_workers/visiblev8/post-processor`).

The architecture of the crawler is heavily inspired (and partially copied from) from [VisibleV8 crawler](https://github.com/wspr-ncsu/visiblev8-crawler)

## Setup

>  [!NOTE]
> This tool requires Python 3.10 or above. If your OS python3 version is <3.10, you can use [`pyenv`](https://github.com/pyenv/pyenv) to setup a specific version of Python.

To setup WebViewTracer crawler install `docker` and `docker-compose`, and run the following command

```sh
pip install -r ./scripts/requirements.txt
python ./scripts/wvt-cli.py setup
```

Subsequently answer the questions asked. The CLI asks for the following information

* *Do you want to setup everything locally or have WebViewTracer connect to remote databases* - Choosing `local` will setup a PostgreSQL server locally. This is the preferred option. Alternatively, if you have a remote PostgresSQL server, you can choose `remote` and answer the subsequent questions which will configure the DB hostname, port, database and database password.

* *How many instances of postprocessors do you want to run?* - This denotes the parallelism used during postprocessing the logs. The default value is `NUM_OF_CPU_CORES * 3`, however, this can be set to a value lower if you have significantly lower Iops speeds on your device or have a older/less powerful CPU.

* *Which directory will you put your apps in?* - By default, this chooses `./apps` as the apps directory, however, this can be changed.

* *What type of devices are you using?* - There are two options here, `physical` or `virtual`. The `virtual` mode only support one device at present and will use a preprepared x86_64 Android emulator image of a Pixel 6a device running Android 13 with VisibleV8WebView 138 to run the apps provided. Note that this has only been tested on a Linux device with KVM support. The physical mode will use the host ADB connections to probe for physical Android devices and will orchestrate docker configurations depending on the number of devices connected. Every single phone is connected to a separate container. Note that you need to manually set up the devices with the VisibleV8WebView when using physical mode and the devices must be connected and reachable on the host machine when the command is run. For our experiment, we used the physical mode.

Once you are done with setup, a `crawl_data` directory, a `raw_logs` and a `parsed_logs` directory should have been created, and your apps directory should contain a set of subdirectories named `split-{number}` corresponding to the number of devices used/detected.

If you plan to use WebViewTracer crawler a lot, you can alias the script to the `wvtcli` command using:

```sh
alias wvtcli="python3 $(pwd)/scripts/wvt-cli.py" 
```

## Run apps

> [!NOTE]
> Make sure that you are able to use `docker` and `docker compose` without using sudo. ([instructions here](https://docs.docker.com/engine/install/linux-postinstall/))

* Download/Extract the apk of the app (For more information on our dataset and how we downloaded apps, navigate to the dataset directory)
* Inside one of the `split-{number}` directories of the apps directory, create a subdirectory corresponding to the name of the app (like `com.imdb.mobile` for IMDB) and place the APK(S) inside the directory
* Run the following

```sh
python3 ./scripts/wvt-cli.py crawl
```

You can observe the app being crawled at `http://0.0.0.0:5901` through a NoVNC server

## Postprocessing the app

Once the app has been crawled, you can postprocess the logs using the following command.

```sh
python3 ./scripts/wvt-cli.py postprocess -p 'com.imdb.mobile' -pp 'Mfeatures+androidflow+exfil+frida'
```

This command instructs the crawler to take the generated logs for `com.imdb.mobile` and postprocess them using the following postprocessors:

* `Mfeatures` - Stands for "mega features", this builds multiple tables that are able to be used to provide aggregrate statistics about the execution of a API or examine specific scripts that use a particular API.

* `androidflow` - This postprocessor takes the log and creates a single table correlating scripts to a sequence of executed APIs alongside a annotation of what kind of API it is (using `./celery_workers/visiblev8/post-processor/android_apis_buckets.json` as a guide). The postprocessor is based on the one proposed by Su et al.[^1] for VV8, used for detecting fingerprinting scripts. In addition to this, `androidflow` also has two more tables, a Java exfil table where it searches for Java interfaces with 'GET', 'POST' or 'REQUEST' in it's arguments and tries to strip out the URL to which the data is being sent to from the arguments and a JavaArgs table which logs the return value and arguments of all Java calls made during the execution of the functions.

* `exfil` - The exfil postprocessor uses the `./celery_workers/visiblev8/post-processor/exfil_apis` file that contains a much more fine grained annotation of the exfiltration APIs mention in the `android_apis_bucket.json` to identify exfiltration APIs and extract the URL and payload, postprocess it and dump it to a table where it can be later queried.

* `frida` - This postprocessor creates two tables, a injection_log and frida_log, frida_log contains a log of all interactions Java code has with WebViews, the injection_log table only contains injections as defined by paper. It also uses `./celery_workers/Third-Party-Library-Names` to resolve the third-party libraries in the stack trace.

There are many more postprocessors available for the VisibleV8 logs at the [VisibleV8 repository](https://github.com/wspr-ncsu/visiblev8/tree/main/post-processor) however, the other postprocessors have not been tested with our current setup.

## Obtaining results

- Run:
```python3 ./scripts/wvt-cli.py results
```

## References

[^1]: Su, Junhua, and Alexandros Kapravelos. ["Automatic discovery of emerging browser fingerprinting techniques."](https://dl.acm.org/doi/10.1145/3543507.3583333) In Proceedings of the ACM Web Conference 2023, pp. 2178-2188. 2023.
