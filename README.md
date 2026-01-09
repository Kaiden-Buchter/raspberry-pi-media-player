# Raspberry Pi 5 Media Player

A complete media player application for Raspberry Pi 5 that plays photos and videos from a Google Drive folder with smooth Ken Burns effects and automatic syncing.

## Features

- **Photo Playback**: Display photos for 10 seconds each with smooth Ken Burns pan and zoom effects
- **Video Playback**: Play videos at their full duration with proper frame rate handling
- **HEIC Support**: Full support for HEIC/HEIF image format from iOS devices
- **Google Drive Integration**: Automatic sync from a shared Google Drive folder every 15 minutes
- **Folder Structure**: Maintains Google Drive folder hierarchy locally
- **Continuous Loop**: Media plays continuously without stopping
- **Fullscreen Display**: Optimized for Raspberry Pi 5 hardware

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Google Drive Setup](#google-drive-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Automatic Startup on Boot](#automatic-startup-on-boot)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

## Requirements

### Hardware
- Raspberry Pi 5
- HDMI display/TV
- Stable internet connection
- Minimum 8GB microSD card (16GB+ recommended)

### Software
- Raspberry Pi OS (Bookworm or later recommended)
- Python 3.9 or higher
- Internet connection for Google Drive sync

## Installation

### Quick Install

1. Clone this repository:
```bash
cd ~
git clone https://github.com/Kaiden-Buchter/raspberry-pi-media-player.git
cd raspberry-pi-media-player
```

2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

The installation script will:
- Update system packages
- Install required system dependencies (SDL2, OpenCV, FFmpeg, HEIF libraries)
- Create a Python virtual environment
- Install all Python dependencies
- Create configuration files
- Set up the media directory

### Manual Installation

If you prefer to install manually:

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y python3 python3-pip python3-venv
sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
sudo apt-get install -y libatlas-base-dev libhdf5-dev libheif-dev ffmpeg
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Create configuration
cp config.yaml.example config.yaml
mkdir -p media
```

## Google Drive Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Click on the project name to ensure it's selected

### Step 2: Enable Google Drive API

1. In the Google Cloud Console, navigate to "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click on it and press "Enable"

### Step 3: Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "+ CREATE CREDENTIALS" and select "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in the required fields (app name, user support email)
   - Add your email as a test user
   - Save and continue through the steps
4. Return to "Credentials" and create OAuth client ID:
   - Application type: "Desktop app"
   - Name: "Raspberry Pi Media Player"
   - Click "Create"
5. Download the credentials JSON file
6. Rename it to `client_secrets.json` and place it in the project directory

### Step 4: Get Your Google Drive Folder ID

1. Open Google Drive in your web browser
2. Navigate to the folder you want to sync
3. Look at the URL - it will look like:
   ```
   https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz
   ```
4. Copy the folder ID (the part after `/folders/`)
5. Make sure the folder is shared appropriately:
   - For personal use: No sharing needed if using your own account
   - For shared folders: Ensure your Google account has access

## Configuration

Edit `config.yaml` to configure the media player:

### Google Drive Settings

```yaml
google_drive:
  folder_id: "YOUR_FOLDER_ID_HERE"  # Replace with your folder ID from Google Drive URL
  local_media_dir: "./media"        # Local directory for synced files
  sync_interval: 15                 # Sync interval in minutes
  client_secrets_file: "client_secrets.json"
```

### Media Player Settings

```yaml
media_player:
  photo_duration: 10          # Seconds to display each photo
  ken_burns_effect: true      # Enable Ken Burns pan/zoom effect
  ken_burns:
    max_zoom: 1.3            # Maximum zoom level (1.3 = 30% zoom)
    steps: 300               # Animation smoothness (higher = smoother)
  shuffle: false             # Randomize playback order
  fullscreen: true           # Run in fullscreen mode
```

## Usage

### First Time Setup

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Start the Google Drive sync (first run will require OAuth authentication):
```bash
python3 gdrive_sync.py
```

On first run:
- A browser window will open for Google authentication
- Log in with your Google account
- Grant permissions to access Google Drive
- The credentials will be saved for future use
- Files will begin syncing to the `media` directory

3. In a separate terminal, start the media player:
```bash
cd ~/raspberry-pi-media-player
source venv/bin/activate
python3 media_player.py
```

### Controls

- **ESC** or **Q**: Quit the media player
- The player runs in fullscreen mode by default
- Mouse cursor is hidden during playback

### Stopping the Applications

- Press `Ctrl+C` in each terminal to stop the applications
- Or press **ESC** or **Q** when the media player window is focused

## Automatic Startup on Boot

**For detailed auto-start instructions, see [docs/AUTOSTART.md](docs/AUTOSTART.md)**

Quick setup - run this command from your installation directory:

```bash
./setup_autostart.sh
```

The script will automatically detect your installation path and username, then install the systemd services.

### Manual Setup (Alternative)

If you prefer to set up manually, edit the service files to match your installation path:

```bash
# Edit user in service files if not using 'pi' user
nano gdrive-sync.service

Then install the services:

```bash
# Copy service files to systemd
sudo cp gdrive-sync.service /etc/systemd/system/
sudo cp media-player.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable gdrive-sync.service
sudo systemctl enable media-player.service

# Start services now
sudo systemctl start gdrive-sync.service
sudo systemctl start media-player.service
```

For more details, troubleshooting, and service management commands, see **[docs/AUTOSTART.md](docs/AUTOSTART.md)**.

```bash
# Check if services are running
sudo systemctl status gdrive-sync.service
sudo systemctl status media-player.service

# View logs
sudo journalctl -u gdrive-sync.service -f
sudo journalctl -u media-player.service -f
```

### Managing Services

```bash
# Stop services
sudo systemctl stop gdrive-sync.service
sudo systemctl stop media-player.service

# Restart services
sudo systemctl restart gdrive-sync.service
sudo systemctl restart media-player.service
## Troubleshooting

### No Media Files Found

**Problem**: Media player shows "No media files found" message

**Solutions**:
1. Check if Google Drive sync is running: `sudo systemctl status gdrive-sync.service`
2. Verify files are syncing to media directory: `ls -la media/`
3. Check sync logs: `sudo journalctl -u gdrive-sync.service -n 50`
4. Ensure Google Drive folder ID is correct in `config.yaml`
5. Verify OAuth authentication completed successfully

### Google Drive Authentication Issues

**Problem**: Can't authenticate with Google Drive

**Solutions**:
1. Ensure `client_secrets.json` exists in the project directory
2. Delete `credentials.json` and try authenticating again
3. Check that Google Drive API is enabled in Google Cloud Console
4. Verify you're listed as a test user in OAuth consent screen
5. For headless setup, run authentication on a machine with a browser, then copy `credentials.json`

### HEIC Images Not Displaying

**Problem**: HEIC/HEIF images from iPhone don't show

**Solutions**:
1. Verify libheif is installed: `dpkg -l | grep libheif`
2. Reinstall pillow-heif: `pip install --upgrade pillow-heif`
3. Check image file isn't corrupted: try opening in another application
4. Ensure file extension is listed in `config.yaml` image formats

### Video Playback Issues

**Problem**: Videos don't play or are choppy

**Solutions**:
1. Check video format is supported (MP4, MOV, AVI, MKV)
2. Verify FFmpeg is installed: `ffmpeg -version`
3. Try reducing video resolution - 4K videos may be too demanding
4. Check system resources: `htop`
5. Ensure video files aren't corrupted

### Display Issues

**Problem**: Black screen or incorrect resolution

**Solutions**:
1. Check HDMI connection
2. Try disabling fullscreen in `config.yaml` and set specific resolution
3. Verify display is detected: `xrandr` or `tvservice -s`
4. Check pygame can access display: `echo $DISPLAY` should show `:0`
5. Ensure X server is running: `ps aux | grep X`

### Performance Issues

**Problem**: Slow or laggy playback

**Solutions**:
1. Reduce Ken Burns effect steps in `config.yaml` (e.g., from 300 to 150)
2. Decrease max zoom level
3. Disable Ken Burns effect entirely: `ken_burns_effect: false`
4. Close other applications to free memory
5. Ensure Raspberry Pi has adequate cooling
6. Check CPU temperature: `vcgencmd measure_temp`

### Service Won't Start on Boot

**Problem**: Autostart services fail

**Solutions**:
1. Check service status: `sudo systemctl status media-player.service`
2. Verify paths in service files are correct
3. Ensure virtual environment exists: `ls -la ~/raspberry-pi-media-player/venv`
4. Check logs: `sudo journalctl -u media-player.service -n 50`
5. Verify user has permissions: service files use `pi` user by default
6. For display issues, ensure X server starts before media player

### Sync Not Working

**Problem**: Files aren't syncing from Google Drive

**Solutions**:
1. Check internet connection: `ping google.com`
2. Verify Google Drive sync service is running
3. Check credentials haven't expired - delete `credentials.json` and re-authenticate
4. Ensure folder ID is correct in `config.yaml`
5. Check available disk space: `df -h`
6. Review sync logs for errors: `tail -f media_player.log`

## Advanced Configuration

### Custom Resolution

To run at a specific resolution instead of fullscreen:

```yaml
media_player:
  fullscreen: false
  resolution: [1920, 1080]  # Width, height
```

### Adjust Sync Interval

To sync more or less frequently:

```yaml
google_drive:
  sync_interval: 30  # Sync every 30 minutes
```

### Shuffle Playback

To randomize media order:

```yaml
media_player:
  shuffle: true
```

### Logging Configuration

Adjust logging verbosity:

```yaml
logging:
  level: "DEBUG"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "media_player.log"
```

### Supported Formats

Add or remove supported formats:

```yaml
media_player:
  video_formats:
    - ".mp4"
    - ".mov"
    - ".avi"
    - ".mkv"
    - ".webm"  # Add WebM support
  
  image_formats:
    - ".jpg"
    - ".jpeg"
    - ".png"
    - ".gif"
    - ".heic"
    - ".HEIC"
    - ".bmp"   # Add BMP support
```

## Project Structure

```
raspberry-pi-media-player/
├── media_player.py          # Main media player application
├── gdrive_sync.py          # Google Drive sync service
├── requirements.txt        # Python dependencies
├── config.yaml.example     # Configuration template
├── config.yaml            # Your configuration (git-ignored)
├── install.sh             # Installation script
├── gdrive-sync.service    # Systemd service for sync
├── media-player.service   # Systemd service for player
├── client_secrets.json    # Google OAuth2 credentials (git-ignored)
├── credentials.json       # Saved Google credentials (git-ignored)
├── media/                 # Synced media files (git-ignored)
└── README.md             # This file
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built for Raspberry Pi 5
- Uses PyDrive2 for Google Drive integration
- Uses pygame and OpenCV for media playback
- Uses pillow-heif for HEIC/HEIF support
