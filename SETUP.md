# Raspberry Pi Media Player - Complete Setup Guide

A complete media player for Raspberry Pi 5 that plays photos and videos from Google Drive with Ken Burns effects and automatic 15-minute syncing.

---

## 🚀 ONE-LINE INSTALLATION (Recommended)

The entire installation can be done with a single command on your Raspberry Pi:

```bash
curl -fsSL https://raw.githubusercontent.com/Kaiden-Buchter/raspberry-pi-media-player/main/setup.sh | bash
```

**Alternative methods if you don't have curl:**

Using `wget`:
```bash
wget -qO- https://raw.githubusercontent.com/Kaiden-Buchter/raspberry-pi-media-player/main/setup.sh | bash
```

Using `git clone`:
```bash
git clone https://github.com/Kaiden-Buchter/raspberry-pi-media-player.git
cd raspberry-pi-media-player
./setup.sh
```

**What this does:**
- Installs curl and git if needed
- Updates system packages
- Installs all system dependencies (SDL2, FFmpeg, HEIF tools)
- Creates Python virtual environment
- Installs Python packages
- Creates media directory
- Sets up configuration files
- **Enables auto-start on reboot** (enabled by default)
- **Schedules daily reboot at 6:00 AM** (enabled by default)

**Installation time:** 10-20 minutes on first run (most time spent downloading packages)

---

## ⚙️ OPTIONAL: Customize During Installation

### Set Google Drive folder ID during install (with curl):

⚠️ **Important:** Use semicolon or newline to separate export from curl:

```bash
export DRIVE_FOLDER="1c0HT9qASuGHynuaiQS07PPvF5D2rUMIa"; curl -fsSL https://raw.githubusercontent.com/Kaiden-Buchter/raspberry-pi-media-player/main/setup.sh | bash
```

Or on separate lines:
```bash
export DRIVE_FOLDER="1c0HT9qASuGHynuaiQS07PPvF5D2rUMIa"
curl -fsSL https://raw.githubusercontent.com/Kaiden-Buchter/raspberry-pi-media-player/main/setup.sh | bash
```

**Note:** `DRIVE_FOLDER` accepts both full URLs and raw folder IDs:
```bash
# Full Drive URL:
export DRIVE_FOLDER="https://drive.google.com/drive/folders/1c0HT9qASuGHynuaiQS07PPvF5D2rUMIa"; curl -fsSL https://raw.githubusercontent.com/Kaiden-Buchter/raspberry-pi-media-player/main/setup.sh | bash

# Or just the raw folder ID:
export DRIVE_FOLDER="1c0HT9qASuGHynuaiQS07PPvF5D2rUMIa"; curl -fsSL https://raw.githubusercontent.com/Kaiden-Buchter/raspberry-pi-media-player/main/setup.sh | bash
```

The script will automatically extract the ID and write it to `config.yaml`.

**🎯 EASIEST METHOD** - Clone locally (no export syntax issues):
```bash
git clone https://github.com/Kaiden-Buchter/raspberry-pi-media-player.git
cd raspberry-pi-media-player
DRIVE_FOLDER="1c0HT9qASuGHynuaiQS07PPvF5D2rUMIa" ./setup.sh
```

Or with wget:
```bash
export DRIVE_FOLDER="1c0HT9qASuGHynuaiQS07PPvF5D2rUMIa"; wget -qO- https://raw.githubusercontent.com/Kaiden-Buchter/raspberry-pi-media-player/main/setup.sh | bash
```

### Disable auto-start on reboot:
```bash
export AUTOSTART=0; curl -fsSL https://raw.githubusercontent.com/Kaiden-Buchter/raspberry-pi-media-player/main/setup.sh | bash
```

Or locally:
```bash
cd ~/raspberry-pi-media-player
AUTOSTART=0 ./setup.sh
```

### Use service account for fully headless auth:
```bash
export SERVICE_ACCOUNT_FILE="/path/to/service_account.json"; curl -fsSL https://raw.githubusercontent.com/Kaiden-Buchter/raspberry-pi-media-player/main/setup.sh | bash
```

Or locally:
```bash
cd ~/raspberry-pi-media-player
SERVICE_ACCOUNT_FILE="/path/to/service_account.json" ./setup.sh
```

### Combine multiple options (locally is simplest):
```bash
cd ~/raspberry-pi-media-player
DRIVE_FOLDER="1c0HT9qASuGHynuaiQS07PPvF5D2rUMIa" SERVICE_ACCOUNT_FILE="/path/to/service_account.json" ./setup.sh
```

Or with curl (use semicolons):
```bash
export DRIVE_FOLDER="1c0HT9qASuGHynuaiQS07PPvF5D2rUMIa"; export SERVICE_ACCOUNT_FILE="/path/to/service_account.json"; curl -fsSL https://raw.githubusercontent.com/Kaiden-Buchter/raspberry-pi-media-player/main/setup.sh | bash
```

---

## 🔑 Google Drive Setup (10 minutes)

### Step 1: Create Google Cloud Project
1. Go to https://console.cloud.google.com
2. Click "Create a new project"
3. Enter project name (e.g., "Media Player")
4. Click "Create"

### Step 2: Enable Google Drive API
1. In the top search bar, search for "Google Drive API"
2. Click the result and click "Enable"

### Step 3: Create OAuth Credentials
1. Go to "APIs & Services" > "Credentials" (left menu)
2. Click "Create Credentials" > "OAuth Client ID"
3. If prompted, click "Configure OAuth Consent Screen"
   - Choose "External" user type
   - Fill in app name (e.g., "Media Player")
   - Add your email to test users
   - Click "Save and Continue" through all screens
4. Back on Credentials page, click "Create Credentials" > "OAuth Client ID" again
5. Select "Desktop application"
6. Click "Create"
7. Click the download icon next to your credential
8. Save the file as `client_secrets.json` in the project directory

### Step 4: Find Your Google Drive Folder
1. Open Google Drive
2. Create or navigate to the folder containing your media
3. Look at the URL: `https://drive.google.com/drive/folders/XXXXXXXXXXXXXXXXXXXXX`
4. Copy the folder ID (the long string after `/folders/`)

### Step 5: Update Configuration
After installation completes, edit the config:

```bash
cd ~/raspberry-pi-media-player
nano config.yaml
```

Update these lines:
```yaml
google_drive:
  folder_id: "YOUR_FOLDER_ID_HERE"  # Paste your folder ID
  auth_mode: "oauth"                 # or "service_account"
```

---

## ▶️ First Run - OAuth Authentication

When you run the sync for the first time with OAuth:

```bash
cd ~/raspberry-pi-media-player
source venv/bin/activate
python3 gdrive_sync.py
```

**What happens:**
1. A browser window opens automatically
2. Log in with your Google account
3. Click "Allow" to grant access
4. The token is saved as `token.json` (don't commit this to git!)
5. Sync starts automatically and runs every 15 minutes

---

## 🔐 Alternative: Service Account (Fully Headless)

If you want zero-interaction auth (useful for deployment):

### Step 1: Create Service Account
1. Go to https://console.cloud.google.com
2. Go to "APIs & Services" > "Credentials"
3. Click "Create Credentials" > "Service Account"
4. Fill in details:
   - Service account name: "Media Player"
   - Click "Create and Continue"
5. Skip the "Grant this service account access to project" section
6. Click "Continue"

### Step 2: Create and Download Key
1. Go to the Services Accounts page
2. Click on the service account you just created
3. Go to the "Keys" tab
4. Click "Add Key" > "Create new key"
5. Choose "JSON"
6. Click "Create"
7. The file downloads automatically as `[name]-[id].json`
8. Rename it to `service_account.json` and place in the project directory

### Step 3: Share Drive Folder
1. Get the service account email from the JSON file:
   ```bash
   grep "client_email" service_account.json
   ```
2. In Google Drive, open your media folder
3. Click "Share" (top right)
4. Paste the service account email
5. Set role to "Viewer"
6. Click "Share"

### Step 4: Update Configuration
```bash
nano config.yaml
```

Update:
```yaml
google_drive:
  folder_id: "YOUR_FOLDER_ID_HERE"
  auth_mode: "service_account"
  service_account_file: "service_account.json"
```

### Step 5: Run Sync (No Browser)
```bash
cd ~/raspberry-pi-media-player
source venv/bin/activate
python3 gdrive_sync.py
```

Runs automatically every 15 minutes with zero user interaction.

---

## 🎬 Features & Controls

**Playback:**
- **Photos:** Displayed for 10 seconds each with smooth Ken Burns pan/zoom effect
- **Videos:** Play at full duration with proper frame rates
- **HEIC Support:** Full support for iOS photos (HEIC/HEIF format)
- **Continuous Loop:** Plays forever without stopping

**Controls:**
- **ESC or Q:** Quit media player
- **Ctrl+C:** Stop sync service

---

## 📋 Verification

After installation, verify everything works:

```bash
cd ~/raspberry-pi-media-player
source venv/bin/activate
python3 test_setup.py
```

---

## 🔄 Auto-Start on Boot

**Already enabled by default** during installation (unless you set `AUTOSTART=0`).

All media player services are grouped under `media-player.target` and start automatically.

To disable auto-start:
```bash
sudo systemctl disable media-player.target
```

To re-enable:
```bash
sudo systemctl enable media-player.target
```

---

## ⏰ Daily Reboot (6:00 AM)

The system is configured to **reboot automatically every day at 6:00 AM** to maintain system health.

The reboot is part of the `media-player.target` group, so it's managed with the other services.

**Check reboot status:**
```bash
sudo systemctl status daily-reboot.timer
sudo systemctl list-timers daily-reboot.timer
```

**Disable only the daily reboot (keep other services running):**
```bash
sudo systemctl disable daily-reboot.timer
sudo systemctl stop daily-reboot.timer
```

**Re-enable:**
```bash
sudo systemctl enable daily-reboot.timer
sudo systemctl start daily-reboot.timer
```

**Change reboot time:**
```bash
sudo systemctl edit daily-reboot.timer
```

Then edit the `OnCalendar` line (examples):
- `06:00` = 6:00 AM
- `03:30` = 3:30 AM
- `20:00` = 8:00 PM

---

## 📊 Manage Services

All services are grouped under **`media-player.target`**. You can manage them together or individually:

**Manage all services at once:**
```bash
sudo systemctl status media-player.target
sudo systemctl start media-player.target
sudo systemctl stop media-player.target
sudo systemctl restart media-player.target
```

**Show all services in media player target:**
```bash
sudo systemctl list-dependencies media-player.target
```

**Manage individual services:**
```bash
sudo systemctl status gdrive-sync.service
sudo systemctl status media-player.service
sudo systemctl status daily-reboot.timer
```

**Start/stop individual services:**
```bash
sudo systemctl start gdrive-sync.service
sudo systemctl stop media-player.service
```

View recent logs:
```bash
sudo journalctl -u gdrive-sync.service -n 50
sudo journalctl -u media-player.service -n 50
```

View reboot timer events:
```bash
sudo systemctl list-timers daily-reboot.timer
```

---

## 🔧 Configuration Options

Edit `config.yaml` to customize:

```yaml
media_player:
  fullscreen: true              # Fullscreen mode
  display_time: 10              # Photo display time (seconds)
  video_formats: ['.mp4', '.mov', '.avi', '.mkv']
  image_formats: ['.jpg', '.png', '.gif', '.heic']
  
google_drive:
  folder_id: "YOUR_FOLDER_ID"
  local_media_dir: "./media"
  auth_mode: "oauth"            # or "service_account"
  delete_local_when_removed: true

sync:
  interval_minutes: 15          # How often to check for new files
  
logging:
  level: "INFO"                 # DEBUG, INFO, WARNING, ERROR
```

---

## ❓ Troubleshooting

### No media files found?
1. Verify `folder_id` in config.yaml is correct
2. Wait for first sync to complete (check logs)
3. Ensure OAuth/service account has permission to folder

**If using service account:**
- Share the folder with the service account email
- Check email in `service_account.json`

### Authentication failed?
1. Ensure `client_secrets.json` is in project directory
2. Delete `token.json` and run again for fresh OAuth login
3. For service account: verify `service_account.json` is valid

### No display output?
1. Check HDMI connection
2. Try `fullscreen: false` in config.yaml
3. Verify display works with other apps

### Player crashes on startup?
1. Check logs: `cat media_player.log`
2. Ensure media directory exists: `mkdir -p media`
3. Verify Python dependencies: `pip list`

### Too many/few files syncing?
- Adjust `video_formats` and `image_formats` in config.yaml
- Check `logging` level for debug info in logs

---

## 📂 Project Structure

```
raspberry-pi-media-player/
├── media_player.py          # Main playback application
├── gdrive_sync.py          # Google Drive sync service
├── setup.sh                # Unified installer (all-in-one)
├── config.yaml.example     # Configuration template
├── requirements.txt        # Python dependencies
├── test_setup.py          # Setup verification script
├── SETUP.md                # Complete setup documentation
└── media/                 # Downloaded media files (created during install)
```

---

## 🚀 Quick Start Summary

1. **Install (one command):**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/Kaiden-Buchter/raspberry-pi-media-player/main/setup.sh | bash
   ```

2. **Download OAuth credentials from Google Cloud Console** and save as `client_secrets.json`

3. **Update config:**
   ```bash
   nano config.yaml
   ```

4. **First run (opens browser for login):**
   ```bash
   cd ~/raspberry-pi-media-player
   source venv/bin/activate
   python3 gdrive_sync.py &
   python3 media_player.py
   ```

5. **Auto-start is already enabled** - reboot and services start automatically

---

## 💡 Tips

- **Multiple folders?** Edit config.yaml and switch `folder_id`, restart services
- **Disable auto-start?** Use `AUTOSTART=0` during bootstrap
- **Update code?** `cd ~/raspberry-pi-media-player && git pull`
- **Remove everything?** `rm -rf ~/raspberry-pi-media-player && sudo systemctl disable gdrive-sync.service media-player.service`

---

**Need help?** Check logs in `media_player.log` or `gdrive_sync.log`, or open an issue on GitHub.
