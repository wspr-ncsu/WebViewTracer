#!/bin/bash

sudo chown -R android ~/.android

while true; do
    emulator -avd Pixel_6a -read-only -no-metrics -no-window
done

wait