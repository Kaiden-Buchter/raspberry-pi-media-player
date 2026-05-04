#!/bin/bash
# Unified installer for Raspberry Pi Media Player
# Combines bootstrap, install, and autostart setup into one script
# Usage: 
#   curl -fsSL https://raw.githubusercontent.com/Kaiden-Buchter/raspberry-pi-media-player/main/setup.sh | bash
#   DRIVE_FOLDER="https://drive.google.com/drive/folders/..." ./setup.sh
#   SERVICE_ACCOUNT_FILE="/path/to/service_account.json" ./setup.sh

set -euo pipefail

# Configuration
REPO_URL="https://github.com/Kaiden-Buchter/raspberry-pi-media-player.git"
INSTALL_DIR="${INSTALL_DIR:-$HOME/raspberry-pi-media-player}"
BRANCH="${BRANCH:-main}"
AUTOSTART="${AUTOSTART:-1}"
ASSUME_YES="${ASSUME_YES:-0}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_step() {
    echo -e "${GREEN}[*]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "=========================================="
echo "Raspberry Pi Media Player - Complete Setup"
echo "=========================================="
echo

# Step 0: Install curl and git if needed
log_step "Checking for required tools..."

if ! command -v git >/dev/null 2>&1 || ! command -v curl >/dev/null 2>&1; then
    log_step "Installing curl and git..."
    sudo apt-get update
    sudo apt-get install -y curl git
fi

# Step 1: Clone or update repo
log_step "Cloning/updating repository..."

if [[ -d "$INSTALL_DIR/.git" ]]; then
    log_step "Updating existing repo at $INSTALL_DIR"
    git -C "$INSTALL_DIR" fetch origin "$BRANCH"
    git -C "$INSTALL_DIR" checkout "$BRANCH"
    git -C "$INSTALL_DIR" pull --ff-only origin "$BRANCH"
else
    log_step "Cloning repo to $INSTALL_DIR"
    git clone --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# Verify we're in the right directory
if [[ ! -f "requirements.txt" || ! -f "gdrive_sync.py" || ! -f "media_player.py" ]]; then
    log_error "Unable to verify project files. Something went wrong with cloning."
    exit 1
fi

# Step 1: Pre-flight checks
log_step "Running pre-flight checks..."

if [[ "$EUID" -eq 0 ]]; then
    log_error "Please run this script as a regular user, not root."
    exit 1
fi

if ! grep -qi "raspberry pi" /proc/cpuinfo 2>/dev/null; then
    if [[ "$ASSUME_YES" -ne 1 ]]; then
        read -r -p "This is optimized for Raspberry Pi. Continue anyway? [y/N]: " reply
        if [[ ! "$reply" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_warning "Not running on Raspberry Pi, but continuing (ASSUME_YES=1)"
    fi
fi

# Step 2: Install system packages
log_step "Installing system dependencies (this may take several minutes)..."
sudo apt-get update
sudo apt-get install -y \
    python3 python3-venv python3-pip \
    build-essential ffmpeg libheif-examples \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libavcodec-dev libavformat-dev libswscale-dev \
    libjpeg-dev zlib1g-dev libfreetype-dev liblcms2-dev libopenjp2-7-dev \
    libtiff-dev libwebp-dev libharfbuzz-dev libfribidi-dev libglib2.0-dev \
    git curl wget >/dev/null 2>&1

log_step "System packages installed"

# Step 3: Create and activate virtual environment
log_step "Creating Python virtual environment..."
python3 -m venv venv
# shellcheck disable=SC1091
source venv/bin/activate

# Step 4: Install Python dependencies
log_step "Installing Python dependencies..."
python -m pip install --upgrade pip setuptools wheel build >/dev/null 2>&1
python -m pip install -r requirements.txt >/dev/null 2>&1

log_step "Python dependencies installed"

# Step 5: Prepare configuration and media directories
log_step "Setting up configuration..."

if [[ ! -f "config.yaml" ]]; then
    cp config.yaml.example config.yaml
    log_step "Created config.yaml (edit this file with your folder ID and auth settings)"
fi

mkdir -p media

# Handle service account setup
if [[ -n "${SERVICE_ACCOUNT_FILE:-}" ]]; then
    if [[ -f "${SERVICE_ACCOUNT_FILE}" ]]; then
        cp "${SERVICE_ACCOUNT_FILE}" service_account.json
        chmod 600 service_account.json
        log_step "Copied service account key from SERVICE_ACCOUNT_FILE"
    else
        log_error "SERVICE_ACCOUNT_FILE does not exist: ${SERVICE_ACCOUNT_FILE}"
        exit 1
    fi
fi

if [[ -n "${SERVICE_ACCOUNT_JSON_B64:-}" ]]; then
    if command -v base64 >/dev/null 2>&1; then
        printf '%s' "${SERVICE_ACCOUNT_JSON_B64}" | base64 -d > service_account.json
        chmod 600 service_account.json
        log_step "Wrote service_account.json from SERVICE_ACCOUNT_JSON_B64"
    else
        log_error "base64 command not found; cannot decode SERVICE_ACCOUNT_JSON_B64"
        exit 1
    fi
fi

# Auto-configure if service account or drive folder provided
if [[ -n "${DRIVE_FOLDER:-}" ]]; then
    log_step "DRIVE_FOLDER detected, configuring..."
elif [[ -f "service_account.json" ]]; then
    log_step "service_account.json found, configuring..."
fi

if [[ -n "${DRIVE_FOLDER:-}" || -f "service_account.json" ]]; then
    python - <<'PY'
import yaml
import re
from pathlib import Path
import os

cfg_path = Path("config.yaml")
cfg = yaml.safe_load(cfg_path.read_text())
gd = cfg.setdefault("google_drive", {})

if os.environ.get("DRIVE_FOLDER"):
    folder_value = os.environ["DRIVE_FOLDER"].strip().strip('/')
    
    # Extract folder ID from URL if needed
    # Handle full URLs like: https://drive.google.com/drive/folders/<ID>?...
    match = re.search(r"/folders/([A-Za-z0-9_-]+)", folder_value)
    if match:
        folder_id = match.group(1)
    else:
        # Assume it's already a raw ID
        folder_id = folder_value
    
    gd["folder_id"] = folder_id
    print(f"  - Set google_drive.folder_id = {folder_id}")

if Path("service_account.json").exists():
    gd["auth_mode"] = "service_account"
    gd["service_account_file"] = "service_account.json"
    print("  - Enabled google_drive.auth_mode=service_account")

cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False))
PY
fi

# Step 6: Verify imports
log_step "Verifying Python imports..."
python - <<'PY'
try:
    import yaml
    import cv2
    import numpy
    import pygame
    print("  - All required modules imported successfully")
except ImportError as e:
    print(f"  - ERROR: {e}")
    exit(1)
PY

# Step 7: Install systemd services (if requested)
if [[ "$AUTOSTART" == "1" ]]; then
    log_step "Setting up systemd autostart services..."
    
    INSTALL_DIR="$(pwd)"
    CURRENT_USER="$(whoami)"
    
    # Create media-player target (groups all services together)
    cat > /tmp/media-player.target << EOF
[Unit]
Description=Raspberry Pi Media Player Services
Documentation=man:systemd.target(5)
After=multi-user.target graphical.target
Wants=gdrive-sync.service media-player.service daily-reboot.timer

[Install]
WantedBy=multi-user.target graphical.target
EOF

    # Create gdrive-sync service
    cat > /tmp/gdrive-sync.service << EOF
[Unit]
Description=Raspberry Pi Media Player - Google Drive Sync
After=network-online.target
Wants=network-online.target
PartOf=media-player.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/gdrive_sync.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=media-player.target
EOF

    # Create media-player service
    cat > /tmp/media-player.service << EOF
[Unit]
Description=Raspberry Pi Media Player
After=graphical.target gdrive-sync.service
Wants=graphical.target
PartOf=media-player.target

[Service]
Type=simple
User=$CURRENT_USER
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/$CURRENT_USER/.Xauthority
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/media_player.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=media-player.target
EOF

    # Create daily reboot timer (6am every day)
    cat > /tmp/daily-reboot.timer << EOF
[Unit]
Description=Daily Reboot at 6am
Documentation=man:systemd.timer(5)
PartOf=media-player.target

[Timer]
OnCalendar=*-*-* 06:00:00
Persistent=true

[Install]
WantedBy=media-player.target
EOF

    # Create daily reboot service
    cat > /tmp/daily-reboot.service << EOF
[Unit]
Description=Reboot the system
After=network.target
PartOf=media-player.target

[Service]
Type=oneshot
ExecStart=/usr/sbin/reboot

[Install]
WantedBy=media-player.target
EOF

    sudo cp /tmp/media-player.target /etc/systemd/system/
    sudo cp /tmp/gdrive-sync.service /etc/systemd/system/
    sudo cp /tmp/media-player.service /etc/systemd/system/
    sudo cp /tmp/daily-reboot.timer /etc/systemd/system/
    sudo cp /tmp/daily-reboot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable media-player.target
    sudo systemctl start media-player.target
    
    log_step "Media Player services installed and enabled"
    log_step "All services grouped under: media-player.target"
    log_step "Services will start automatically on reboot"
    log_step "System will reboot daily at 6:00 AM"
    
    rm -f /tmp/media-player.target /tmp/gdrive-sync.service /tmp/media-player.service /tmp/daily-reboot.timer /tmp/daily-reboot.service
fi

# Final summary
echo
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo
echo "📁 Project directory: $INSTALL_DIR"
echo
echo "📋 Next steps:"
echo "   1. Edit config.yaml with your Google Drive folder ID:"
echo "      nano $INSTALL_DIR/config.yaml"
echo
echo "   2. For OAuth (browser login):"
echo "      - Download client_secrets.json from Google Cloud Console"
echo "      - Save to: $INSTALL_DIR/client_secrets.json"
echo
echo "   3. For Service Account (headless):"
echo "      - Already configured if SERVICE_ACCOUNT_FILE was provided"
echo "      - Share your Drive folder with the service account email"
echo
echo "   4. Start the sync (first run opens browser for login):"
echo "      cd $INSTALL_DIR"
echo "      source venv/bin/activate"
echo "      python3 gdrive_sync.py"
echo
echo "   5. In another terminal, start the media player:"
echo "      cd $INSTALL_DIR"
echo "      source venv/bin/activate"
echo "      python3 media_player.py"
echo
if [[ "$AUTOSTART" == "1" ]]; then
    echo "   6. All services grouped under 'media-player.target'. Check status:"
    echo "      sudo systemctl status media-player.target"
    echo "      sudo systemctl list-units --target=media-player.target"
    echo
    echo "   7. Individual service status:"
    echo "      sudo systemctl status gdrive-sync.service"
    echo "      sudo systemctl status media-player.service"
    echo "      sudo systemctl status daily-reboot.timer"
    echo
fi
echo "📚 Full documentation: See SETUP.md in the project directory"
echo "=========================================="
echo
