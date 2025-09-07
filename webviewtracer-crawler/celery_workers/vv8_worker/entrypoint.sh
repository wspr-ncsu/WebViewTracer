#!/bin/bash
sudo chown -R android /app/
sudo chmod -R ugo+rwx /app/
# Start noVNC and VNC server
/opt/noVNC/utils/novnc_proxy --vnc localhost:$VNC_PORT --listen $NO_VNC_PORT &
vncserver $DISPLAY -depth $VNC_COL_DEPTH -geometry $VNC_RESOLUTION -SecurityTypes None -localhost no --I-KNOW-THIS-IS-INSECURE &

# Conditionally start the appropriate ADB service
if [ "$ADB_SETUP" = "virtual" ]; then
    /app/emulator.sh &
    /app/scrcpy-service.sh &
    /app/logcat-service.sh &
else
    /app/adb-service.sh &
fi

export PYTHONUNBUFFERED=TRUE

# Wait for the emulator/services to be fully ready
sleep 190

# Start VV8 UI Harvester jobs
cd /app/vv8_worker/uiharvester
python3 -u execution_wrapper/main.py -p /app/vv8_worker/apps -m auto -r 5
python3 -u execution_wrapper/main.py -p /app/vv8_worker/apps -m auto -r 10 -retryFailedApps

# Wait for background processes
wait