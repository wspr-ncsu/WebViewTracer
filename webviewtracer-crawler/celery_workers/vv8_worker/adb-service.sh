#!/bin/bash

while true
do
    adb --one-device $ANDROID_ID server nodaemon
done