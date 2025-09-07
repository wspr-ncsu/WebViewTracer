#!/bin/bash
# Ignore the name of this file it definitely does not nuke the Documents folders of a app
command -v adb >/dev/null 2>&1 || { echo "ADB is not installed. Please install ADB first."; exit 1; }

delete_files() {
  adb shell "rm -rf /sdcard/Documents/*"
}

check_files() {
  FILES_EXIST=$(adb shell "ls /sdcard/Documents/")
  if [ -z "$FILES_EXIST" ]; then
    echo "All files in /sdcard/Documents/ have been successfully deleted."
    return 0
  else
    echo "Files still exist in /sdcard/Documents/."
    return 1
  fi
}

while true; do
  delete_files
  check_files
  if [ $? -eq 0 ]; then
    break
  fi
done
