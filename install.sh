#!/bin/bash
# Installation script for Raspberry Pi 5 Media Player
# This script installs all dependencies and sets up the media player

set -e  # Exit on error

echo "=========================================="
echo "Raspberry Pi 5 Media Player Installation"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This script is optimized for Raspberry Pi 5"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Please do not run this script as root (without sudo)"
    exit 1
fi

echo "Step 1: Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo "Step 2: Installing system dependencies..."
# Install Python 3 and pip
sudo apt-get install -y python3 python3-pip python3-venv

# Install SDL dependencies for pygame
sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# Install OpenCV dependencies
sudo apt-get install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev libharfbuzz0b libwebp7 libjasper1
sudo apt-get install -y libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt-get install -y libilmbase-dev libopenexr-dev libgstreamer1.0-dev

# Install image processing libraries
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install -y libxvidcore-dev libx264-dev

# Install HEIF/HEIC support
sudo apt-get install -y libheif-dev

# Install ffmpeg for video support
sudo apt-get install -y ffmpeg

echo ""
echo "Step 3: Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo ""
echo "Step 4: Installing Python dependencies..."
pip install --upgrade pip
pip install wheel
pip install -r requirements.txt

echo ""
echo "Step 5: Creating configuration files..."
if [ ! -f "config.yaml" ]; then
    cp config.yaml.example config.yaml
    echo "Created config.yaml - Please edit this file with your settings"
else
    echo "config.yaml already exists - skipping"
fi

echo ""
echo "Step 6: Creating media directory..."
mkdir -p media
echo "Media directory created at: $(pwd)/media"

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Set up Google Drive OAuth2 credentials:"
echo "   - Go to https://console.cloud.google.com"
echo "   - Create a new project or select an existing one"
echo "   - Enable the Google Drive API"
echo "   - Create OAuth2 credentials (Desktop application)"
echo "   - Download the credentials and save as 'client_secrets.json'"
echo ""
echo "2. Edit config.yaml:"
echo "   - Set your Google Drive folder ID"
echo "   - Adjust media player settings as needed"
echo ""
echo "3. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "4. Start the Google Drive sync service:"
echo "   python3 gdrive_sync.py"
echo ""
echo "5. In another terminal, start the media player:"
echo "   source venv/bin/activate"
echo "   python3 media_player.py"
echo ""
echo "For automatic startup on boot, see the README.md"
echo ""
