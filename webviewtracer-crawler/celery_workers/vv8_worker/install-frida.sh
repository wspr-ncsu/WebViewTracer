#!/bin/bash
adb shell su -c "kill -9 $(adb shell su -c 'pidof frida-server')"
adb push /app/frida-server /data/local/tmp/
adb shell su -c ''
frida-ps -U