#!/bin/bash
set -euo pipefail

echo "[*] Setting up Python virtualenv..."
python3 -m venv env
source env/bin/activate

echo "[*] Installing dependencies..."
pip install --upgrade pip
pip install -r scripts/requirements.txt

echo "[*] Running initial CLI check..."
python3 ./scripts/wvt-cli.py || true

echo "[*] Downloading AVD emulator image..."
mkdir -p celery_workers/avd
curl -L -o avd.zip "https://zenodo.org/record/16028902/files/avd.zip"
unzip -o avd.zip -d celery_workers/avd/

echo "[*] Running wvt-cli setup (press enter for defaults)..."
python3 ./scripts/wvt-cli.py setup

echo "[*] Downloading and unpacking sample apps..."
mkdir -p apps/split_1
curl -L -o apps.zip "https://zenodo.org/record/16028902/files/apps_x86_64.zip"
unzip -o apps.zip -d apps/split_1/

echo "[*] Starting crawl..."
if ! python3 ./scripts/wvt-cli.py crawl; then
    echo "[*] Python crawl failed, using docker-compose fallback..."
    docker compose --env-file .env up --build -d -V --force-recreate --remove-orphans
fi

URL="http://0.0.0.0:6901"
echo "[*] Opening http://0.0.0.0:6901 to observe the crawl."
xdg-open "$URL" >/dev/null 2>&1 || echo "Could not auto-open browser, please visit $URL manually."