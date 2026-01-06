#!/bin/bash
# Script to install systemd services for automatic startup
# Run this after completing the initial setup and testing

set -e

echo "=========================================="
echo "Systemd Service Installation"
echo "=========================================="
echo ""

# Get current directory
INSTALL_DIR=$(pwd)
CURRENT_USER=$(whoami)

echo "Installation directory: $INSTALL_DIR"
echo "User: $CURRENT_USER"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run install.sh first."
    exit 1
fi

# Check if config exists
if [ ! -f "config.yaml" ]; then
    echo "Error: config.yaml not found!"
    echo "Please copy config.yaml.example to config.yaml and configure it."
    exit 1
fi

# Check if client_secrets exists
if [ ! -f "client_secrets.json" ]; then
    echo "Warning: client_secrets.json not found!"
    echo "You need this file for Google Drive sync."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Creating service files..."

# Create gdrive-sync service
cat > /tmp/gdrive-sync.service << EOF
[Unit]
Description=Raspberry Pi Media Player - Google Drive Sync
After=network-online.target
Wants=network-online.target

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
WantedBy=multi-user.target
EOF

# Create media-player service
cat > /tmp/media-player.service << EOF
[Unit]
Description=Raspberry Pi Media Player
After=graphical.target gdrive-sync.service
Wants=graphical.target

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
WantedBy=graphical.target
EOF

echo "Installing service files..."
sudo cp /tmp/gdrive-sync.service /etc/systemd/system/
sudo cp /tmp/media-player.service /etc/systemd/system/

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling services..."
sudo systemctl enable gdrive-sync.service
sudo systemctl enable media-player.service

echo ""
echo "Services installed successfully!"
echo ""
echo "To start the services now:"
echo "  sudo systemctl start gdrive-sync.service"
echo "  sudo systemctl start media-player.service"
echo ""
echo "To check service status:"
echo "  sudo systemctl status gdrive-sync.service"
echo "  sudo systemctl status media-player.service"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u gdrive-sync.service -f"
echo "  sudo journalctl -u media-player.service -f"
echo ""
echo "To stop services:"
echo "  sudo systemctl stop gdrive-sync.service"
echo "  sudo systemctl stop media-player.service"
echo ""
echo "To disable autostart:"
echo "  sudo systemctl disable gdrive-sync.service"
echo "  sudo systemctl disable media-player.service"
echo ""

# Clean up temp files
rm /tmp/gdrive-sync.service /tmp/media-player.service

echo "Done!"
