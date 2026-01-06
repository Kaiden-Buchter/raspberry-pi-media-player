# Quick Start Guide

This is a condensed guide to get your Raspberry Pi Media Player up and running quickly.

## Prerequisites

- Raspberry Pi 5 with Raspberry Pi OS installed
- Internet connection
- Google account with access to Google Drive

## Installation (5 minutes)

```bash
# Clone the repository
cd ~
git clone https://github.com/Kaiden-Buchter/raspberry-pi-media-player.git
cd raspberry-pi-media-player

# Run installation
chmod +x install.sh
./install.sh
```

Wait for installation to complete (may take 10-15 minutes on first run).

## Google Drive Setup (10 minutes)

### 1. Create Google Cloud Project
- Go to https://console.cloud.google.com
- Create a new project
- Enable "Google Drive API"

### 2. Get OAuth2 Credentials
- Go to "APIs & Services" > "Credentials"
- Create "OAuth client ID" (Desktop app)
- Download JSON file
- Save as `client_secrets.json` in project directory

### 3. Get Folder ID
- Open Google Drive
- Navigate to your media folder
- Copy ID from URL: `drive.google.com/drive/folders/YOUR_ID_HERE`

## Configuration (2 minutes)

```bash
# Copy example config
cp config.yaml.example config.yaml

# Edit configuration
nano config.yaml
```

Update these settings:
- `google_drive.folder_id`: Your Google Drive folder ID
- Adjust other settings as needed

## First Run

### Terminal 1: Start Sync
```bash
source venv/bin/activate
python3 gdrive_sync.py
```

First time will open browser for Google authentication. Follow prompts.

### Terminal 2: Start Player
```bash
source venv/bin/activate
python3 media_player.py
```

## Enable Auto-Start

```bash
# Update service files if needed
sudo cp gdrive-sync.service /etc/systemd/system/
sudo cp media-player.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable gdrive-sync.service media-player.service
sudo systemctl start gdrive-sync.service media-player.service
```

## Controls

- **ESC** or **Q**: Quit player
- **Ctrl+C**: Stop sync service

## Verify Installation

```bash
source venv/bin/activate
python3 test_setup.py
```

## Common Issues

**No media files?**
- Wait for first sync to complete (check sync logs)
- Verify folder ID is correct

**Authentication failed?**
- Ensure `client_secrets.json` is in project directory
- Delete `credentials.json` and try again

**Display issues?**
- Check HDMI connection
- Try `fullscreen: false` in config

## Full Documentation

See [README.md](README.md) for complete documentation, troubleshooting, and advanced configuration.
