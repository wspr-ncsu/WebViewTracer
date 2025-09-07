## Requirements:
* Python 3.8.10

> For Record&replay the following additional requirements are needed  
* javac ≥ 11.0.22
* java ≥ 14.0.2

> For Activities the following additional requirements are needed
* apktool ≥ 2.9.3

## Set up UIHarvester apk
* Install UIHarvester apk

```sh
  adb install -g ./Service/UIHarvesterService.apk
```
* Enable UIHarvester Service

  Navigate to Settings-->Accesibility and enable UIHarvesterService 

* Set logcat buffer to to 4M or 16M

  Developer options-->Logger buffer sizes

* Set lock screen to None
 
  Options-->Security-->Screen "None"

* (Optional) Set Default USB configuration to "File transfer / Android Auto" from the developer options   

## Set up Frida 
* Push Frida Server to the device

* Start Frida Server

## Traverse apps
* Install an android app (e.g., com.imdb.mobile) using "adb instal -g" option. The -g option approves all the app's permission at installation. UIHarvester does NOT handle app's run-time permissions in order to simplify the traversing procedure (Either install apps using "adb install -g"  to approve all permissions at installation or the traversing.py will try to programmatically approve all the permissions for a given app before traversing it.)

  ```
  adb install -g com.imdb.mobile.apk
  ```

  In case of multiple apks for one app use the command

  ```
  adb install-multiple -g *.apk
  ```

* Run traversing.py

  ```
  python3 traversing.py -p com.imdb.mobile -d 99241FFAZ002FF -e BFS -o com.imdb.mobile -s 2 -a 3 -t 45 -w 1
  ```
  
* Check traversing.py --help for options

## Examples

* Example 1

Traverse imdb using BFS for 135 seconds, with a 2 seconds delay between clicks and 4 seconds sleep time to launch the main activity. 

```
python3 traversing.py -p com.imdb.mobile -d 99241FFAZ002FF -e BFS -o com.imdb.mobile -s 3 -a 4 -t 135
```

Option -fl can be used to load other frida scripts.

```
python3 traversing.py -p com.imdb.mobile -d 99241FFAZ002FF -e BFS -o com.imdb.mobile -s 3 -a 4 -t 135 -fl script1.js script2.js
```

Option -G 1 will try to login using Google's SSO if such element is found on the screen (works only for DFS & BFS). 

```
python3 traversing.py -p com.imdb.mobile -d 99241FFAZ002FF -e BFS -o com.imdb.mobile -s 3 -a 4 -t 135 -G 1
```


* Example 2.a 

Manually traverse imdb using record&replay option and save records to file 

```
python3 traversing.py -p com.imdb.mobile -d 99241FFAZ002FF --record ./saved_records
```
* Example 2.b

Replay a previous recorded path using record&replay option

```
python3 traversing.py -p com.imdb.mobile -d 99241FFAZ002FF --replay ./saved_records
```
* Example 3

Option -w 1  waits for the app's webviews to load before interacting with the current elements on the screen and prints the stacktrace for functions such as loadurl()  

```
python3 traversing.py -p com.imdb.mobile -d 99241FFAZ002FF -e BFS -o com.imdb.mobile -s 3 -a 4 -t 135 -w 1
```

## Logfiles

Frida logs can be found at ./results/"app-package-name"/frida/logfile

Activities logs can be found at ./results/"app-package-name"/Activities/

UIHarvester logs can be found at ./results/"app-package-name"/UIHarvester/

Full logcat can be found at ./results/"app-package-name"/logcat/full_logcat

## Activities

UIHarvester identifies and traverses app activities using the option --activities.

Using this option the UIHarvester logs are splitted based on the app's activities.

Logs provide information about which activities have been identified and succesfully opened.

## Custom Tabs

Identifying elements from CustomTabs is supported for browsers *chrome* and *chromium*  

## Troubleshooting

* UIHarvester does NOT handle app's run-time permissions in order to simplify the traversing procedure. Either install apps using "adb install -g" to approve all permissions at installation or the traversing.py will try to programmatically approve all the permissions for a given app.  

* If ElementsList is empty and the traversing.py does not show elements set the logcat buffer to 4M or 16M

* If traversing.py does not open the app, try to restart frida server

* In order to display elements from the screen for a given app without using the traversing.py, set the current app to the specific package name (e.g., com.imdb.mobile) in UIHarvester

    ```adb shell "su -c 'echo com.imdb.mobile > /data/data/reaper.UIHarvester/current_app'" ```  

* To display elements in logcat in plaintext format

    ```adb shell "su -c 'echo true > /data/data/reaper.UIHarvester/is_plaintext'" ```

* To display elements in logcat in base64 format

    ```adb shell "su -c 'echo false > /data/data/reaper.UIHarvester/is_plaintext'" ```

* App's may ask to input additionall info when loging with Google's SSO (e.g., age, sex, etc ). This procedure can not be automated as it is not generic across apps. 

* If the app doesn't let UIHarvester take a screenshot use this option 
    
    ``` -fl ./frida-scripts/disableSecureFlag.js ```

## Devices & Android versions tested

* Pixel 4 & Pixel 4a - Android versions: 11 & 13 (traversing & Google's SSO)

* Pixel 6 - Android version 14 (traversing only - Google's SSO is not working) 
