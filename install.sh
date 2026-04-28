#!/bin/bash
# One-step installer for Raspberry Pi Media Player

set -euo pipefail

ASSUME_YES=0
ENABLE_AUTOSTART=0

for arg in "$@"; do
    case "$arg" in
        --yes|-y)
            ASSUME_YES=1
            ;;
        --autostart)
            ENABLE_AUTOSTART=1
            ;;
        *)
            echo "Unknown argument: $arg"
            echo "Usage: ./install.sh [--yes|-y] [--autostart]"
            exit 1
            ;;
    esac
done

echo "=========================================="
echo "Raspberry Pi Media Player One-Step Install"
echo "=========================================="
echo

if [[ ! -f "requirements.txt" || ! -f "gdrive_sync.py" || ! -f "media_player.py" ]]; then
    echo "Run this script from the project directory."
    exit 1
fi

if [[ "$EUID" -eq 0 ]]; then
    echo "Please run as a regular user, not root."
    exit 1
fi

if ! grep -qi "raspberry pi" /proc/cpuinfo 2>/dev/null && [[ "$ASSUME_YES" -ne 1 ]]; then
    read -r -p "This is optimized for Raspberry Pi. Continue? [y/N]: " reply
    if [[ ! "$reply" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "[1/5] Installing system packages..."
sudo apt-get update
sudo apt-get install -y \
    python3 python3-venv python3-pip \
    build-essential ffmpeg libheif-examples \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libavcodec-dev libavformat-dev libswscale-dev \
    libjpeg-dev zlib1g-dev libfreetype-dev liblcms2-dev libopenjp2-7-dev \
    libtiff-dev libwebp-dev libharfbuzz-dev libfribidi-dev libglib2.0-dev

echo "[2/5] Creating virtual environment..."
python3 -m venv venv
# shellcheck disable=SC1091
source venv/bin/activate

echo "[3/5] Installing Python dependencies..."
python -m pip install --upgrade pip setuptools wheel build
python -m pip install -r requirements.txt

echo "[4/5] Preparing config and media directories..."
if [[ ! -f "config.yaml" ]]; then
    cp config.yaml.example config.yaml
    echo "Created config.yaml"
fi
mkdir -p media

if [[ -n "${DRIVE_FOLDER:-}" ]]; then
    python - <<'PY'
import yaml
from pathlib import Path

cfg_path = Path("config.yaml")
cfg = yaml.safe_load(cfg_path.read_text())
cfg.setdefault("google_drive", {})["folder_id"] = __import__("os").environ["DRIVE_FOLDER"]
cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False))
print("Set google_drive.folder_id from DRIVE_FOLDER")
PY
fi

echo "[5/5] Verifying Python imports..."
python - <<'PY'
import yaml, cv2, numpy, pygame
print("OK: yaml, cv2, numpy, pygame imports successful")
PY

if [[ "$ENABLE_AUTOSTART" -eq 1 ]]; then
    echo
    echo "Enabling systemd autostart..."
    ./setup_autostart.sh --yes
fi

echo
echo "=========================================="
echo "Install complete"
echo "=========================================="
echo "1) Put OAuth credentials in client_secrets.json"
echo "2) Set google_drive.folder_id in config.yaml (or use DRIVE_FOLDER env var)"
echo "3) Run: source venv/bin/activate && python3 gdrive_sync.py"
echo "4) Run: source venv/bin/activate && python3 media_player.py"
