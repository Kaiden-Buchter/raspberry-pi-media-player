#!/bin/bash
# One-command bootstrap installer
# Usage examples:
#   curl -fsSL https://raw.githubusercontent.com/Kaiden-Buchter/raspberry-pi-media-player/main/bootstrap.sh | bash
#   DRIVE_FOLDER="https://drive.google.com/drive/folders/..." curl -fsSL ... | bash

set -euo pipefail

REPO_URL="https://github.com/Kaiden-Buchter/raspberry-pi-media-player.git"
INSTALL_DIR="${INSTALL_DIR:-$HOME/raspberry-pi-media-player}"
BRANCH="${BRANCH:-main}"
AUTOSTART="${AUTOSTART:-1}"

if command -v git >/dev/null 2>&1; then
    :
else
    sudo apt-get update
    sudo apt-get install -y git
fi

if [[ -d "$INSTALL_DIR/.git" ]]; then
    echo "Updating existing repo at $INSTALL_DIR"
    git -C "$INSTALL_DIR" fetch origin "$BRANCH"
    git -C "$INSTALL_DIR" checkout "$BRANCH"
    git -C "$INSTALL_DIR" pull --ff-only origin "$BRANCH"
else
    echo "Cloning repo to $INSTALL_DIR"
    git clone --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
chmod +x install.sh
if [[ "$AUTOSTART" == "1" ]]; then
    ./install.sh --yes --autostart
else
    ./install.sh --yes
fi

echo
echo "Bootstrap complete."
echo "Project directory: $INSTALL_DIR"
