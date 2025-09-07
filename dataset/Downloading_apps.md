## Requirements:	
* DummyDroid v3.0
* Raccoon v4.24.0
* Android device
* Gmail account

## Setup:
A. Open DummyDroid `java -jar dummydroid-3.0.jar`
1. Fill the fields in DummyDroid `java -jar dummydroid-3.0.jar`: 
* Model
```sh
    adb shell getprop ro.product.model
```
* Manufacturer
```sh
    adb shell getprop ro.product.manufacturer
```
* Brand
```sh
   adb shell getprop ro.product.brand 
```
* Product
```sh
    adb shell getprop ro.product.name
```
* Device
```sh
    adb shell getprop ro.product.device
```
* Hardware
```sh
    adb shell getprop ro.hardware
```
* Id
```sh
    adb shell getprop ro.product.id
```
or
```sh
    adb shell getprop ro.build.id
```
* Release version
```sh
    adb shell getprop ro.build.version.release
```
* Fingerprint
```sh
    adb shell getprop ro.build.fingerprint 
```

    
2. Enter Google account credentials in Uplink Terminal
* Click Login account

* If log says "Failure To access your account, you must sign in on the web."

    -Copy paste the url of the above message in your browser and login (we need to insert the oauth token to dummydroid - needs to be done quickly)

    -Open Console - Storage - Cookies and find oauthtoken. Copy the value (you may have two values check which one works with the following steps)

    -Paste the value in Dummydroid under Uplink-->Web login flow

    -Click Login account. Succesfull login wll show the values (save them as they are needed for the Raccoon profile)

      Account: ...
      Name: ...
      Email: ...
      Auth Token: ...
      Services:...
  
  (More info in https://raccoon.onyxbits.de/blog/needs-browser-login-workaround/)

* Click Register GSF ID. Succesfull registration will show the values: (save them as they are needed for the Raccoon profile)
    GSF ID: ...
    User Agent: ...

3. Store the above values and close DummyDroid

B. Get the GSF ID (we need the GSF ID of the device, not the one provided by Raccoon)
* For rooted device 
    ```sh
    adb shell
    ```
    ```sh
    su
    cp /data/data/com.google.android.gsf/databases/gservices.db /sdcard/Download
    ```
    ```sh
    adb pull /sdcard/Download/gservices.db .
    printf '%x\n' $(sqlite3 gservices.db "select * from main where name = \"android_id\";" | cut -d'|' -f2)
    ```
C. Open Raccoon and set the directory to save the apps

```sh
    java -Draccoon.homedir=. -Draccoon.home=./apps/ -jar raccoon4.jar
```
    
* Login with your Gmail Credentials
    
* If Raccoon says "NeedsBrowser"

   -Close Raccoon

   -Edit /apps/content/database/raccoondb_4.script

   -Append the following 2 lines in the raccoondb_4.script

```
INSERT INTO PLAYPROFILES VALUES('test_account','test_account@gmail.com','test_Auth_Token','test_User_Agent',NULL,0,NULL,NULL,'test_GSFID','test_password')
```

```
INSERT INTO VARIABLES VALUES('playprofile','test_account')
```
Example Gmail account creds to be used in the above lines in the raccoon database:

    email: test_account@gmail.com
    password: test_password
    Auth Token: test_Auth_Token (get from step A.2)
    User Agent: test_User_Agent (get from step A.2)
    GSF ID : test_GSFID (get from step B)

* Download an app using the Raccoon program to test if everything works

* Close Raccoon and use downloader.py to download apks from a list of package names (step D) 

D. Download apps using python3 downloader.py <RACCOON_HOMEDIR> <APPS' PACKAGE NAMES FILE>

* Example:
    ```sh
    python3 downloader.py . ./app_packagenames
    ```
    - We set the <RACCOON_HOMEDIR> to . because in step C the Draccoon.homedir is the working directory "."
    - Fill the ./app_packagenames file with  the package names you want to download (one line per package name)
    - The apks are downloaded inside ./apps/content/apps/
    - Multiple apks may exists inside each packagename folder. Install each Android application using adb install-multiple *.apk
