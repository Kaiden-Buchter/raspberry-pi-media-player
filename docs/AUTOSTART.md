# Auto-Start on Boot

This guide explains how to configure the Raspberry Pi Media Player to start automatically when your Raspberry Pi boots up.

## Prerequisites

Before enabling auto-start, make sure:

1. ✅ The media player is working correctly when run manually
2. ✅ Google Drive sync is working and authenticated
3. ✅ You have tested both `media_player.py` and `gdrive_sync.py` successfully
4. ✅ Your `config.yaml` is properly configured
5. ✅ Your `client_secrets.json` and `credentials.json` are in place

## Quick Setup (Recommended)

The easiest way to enable auto-start is to use the provided setup script:

```bash
cd /home/wyorobotics/Desktop/raspberry-pi-media-player-main
./setup_autostart.sh
```

This script will:
- Automatically detect your installation directory and username
- Create systemd service files with the correct paths
- Install and enable the services
- Show you helpful commands for managing the services

**That's it!** After running this script, the media player will start automatically on boot.

## What Gets Installed

The setup installs two systemd services:

### 1. gdrive-sync.service
- Starts after network is available
- Runs the Google Drive sync in the background
- Auto-restarts if it crashes

### 2. media-player.service  
- Starts after the graphical interface is ready
- Waits for gdrive-sync to start first
- Runs the media player on your display
- Auto-restarts if it crashes

## Managing the Services

### Check Service Status

```bash
sudo systemctl status gdrive-sync.service
sudo systemctl status media-player.service
```

### Start Services Manually

```bash
sudo systemctl start gdrive-sync.service
sudo systemctl start media-player.service
```

### Stop Services

```bash
sudo systemctl stop media-player.service
sudo systemctl stop gdrive-sync.service
```

### Restart Services

```bash
sudo systemctl restart gdrive-sync.service
sudo systemctl restart media-player.service
```

### Disable Auto-Start

If you want to disable auto-start on boot but keep the services installed:

```bash
sudo systemctl disable gdrive-sync.service
sudo systemctl disable media-player.service
```

To re-enable:

```bash
sudo systemctl enable gdrive-sync.service
sudo systemctl enable media-player.service
```

### Remove Services Completely

```bash
# Stop and disable the services
sudo systemctl stop media-player.service
sudo systemctl stop gdrive-sync.service
sudo systemctl disable media-player.service
sudo systemctl disable gdrive-sync.service

# Remove the service files
sudo rm /etc/systemd/system/media-player.service
sudo rm /etc/systemd/system/gdrive-sync.service

# Reload systemd
sudo systemctl daemon-reload
```

## Viewing Logs

Logs are helpful for troubleshooting if something isn't working:

### View Recent Logs

```bash
# Last 50 lines of gdrive-sync logs
sudo journalctl -u gdrive-sync.service -n 50

# Last 50 lines of media-player logs
sudo journalctl -u media-player.service -n 50
```

### Follow Logs in Real-Time

```bash
# Watch gdrive-sync logs live
sudo journalctl -u gdrive-sync.service -f

# Watch media-player logs live
sudo journalctl -u media-player.service -f
```

### View Logs Since Boot

```bash
sudo journalctl -u media-player.service -b
```

## Troubleshooting

### Service Won't Start

**Check the service status first:**
```bash
sudo systemctl status media-player.service
```

**Common issues:**

1. **Wrong paths**: Make sure the service files have the correct installation directory
   - Check with: `cat /etc/systemd/system/media-player.service`
   - Should show your actual installation path

2. **Python environment issues**: Verify the virtual environment exists
   ```bash
   ls -la /home/wyorobotics/Desktop/raspberry-pi-media-player-main/venv
   ```

3. **Display not ready**: The media player needs the graphical interface
   - Check if X server is running: `echo $DISPLAY`
   - Try running manually first: `python3 media_player.py`

4. **Permission issues**: Make sure the user in the service file matches your username
   ```bash
   whoami  # Should show 'wyorobotics'
   ```

### Display Issues on Boot

If the media player doesn't show on your display:

1. **Check DISPLAY variable**:
   ```bash
   # The service should have DISPLAY=:0
   # Check with:
   sudo systemctl cat media-player.service | grep DISPLAY
   ```

2. **Check XAUTHORITY**:
   The service needs access to X server. Verify the path:
   ```bash
   ls -la ~/.Xauthority
   ```

3. **Wait for graphical interface**:
   The service is configured to wait for `graphical.target`, but sometimes you need to add a small delay. If issues persist, you can edit the service to add a delay.

### Google Drive Sync Not Working

1. **Check credentials**:
   ```bash
   ls -la /home/wyorobotics/Desktop/raspberry-pi-media-player-main/credentials.json
   ```

2. **Check network**:
   ```bash
   ping -c 3 google.com
   ```

3. **View sync logs**:
   ```bash
   sudo journalctl -u gdrive-sync.service -n 100
   ```

### Services Start But Media Player Shows Black Screen

1. **Check media files exist**:
   ```bash
   ls -la /home/wyorobotics/Desktop/raspberry-pi-media-player-main/media/
   ```

2. **Wait for sync**:
   Give the sync service a few minutes to download files on first boot

3. **Check config.yaml**:
   ```bash
   cat /home/wyorobotics/Desktop/raspberry-pi-media-player-main/config.yaml
   ```

## Manual Service Installation

If you prefer to install manually instead of using `setup_autostart.sh`:

### Step 1: Create Service Files

The static service files in the repository are templates. You need to use `setup_autostart.sh` or manually create them with your paths:

```bash
# Navigate to your installation directory
cd /home/wyorobotics/Desktop/raspberry-pi-media-player-main

# The setup_autostart.sh script will automatically create service files
# with your current directory and username
./setup_autostart.sh
```

### Step 2: If You Want to Manually Edit

If you need to manually edit the installed services:

```bash
# Edit the installed service files
sudo nano /etc/systemd/system/media-player.service
sudo nano /etc/systemd/system/gdrive-sync.service

# After editing, reload systemd
sudo systemctl daemon-reload

# Restart the services
sudo systemctl restart gdrive-sync.service
sudo systemctl restart media-player.service
```

## Advanced Configuration

### Change Restart Behavior

The services are configured to restart automatically on failure. To change this:

```bash
sudo nano /etc/systemd/system/media-player.service
```

Change `Restart=always` to one of:
- `Restart=no` - Never restart
- `Restart=on-failure` - Only restart on failure
- `Restart=always` - Always restart (current setting)

### Adjust Restart Delay

Current delay is 10 seconds (`RestartSec=10`). You can increase or decrease this value.

### Run on Different Display

If you have multiple displays:

```bash
sudo nano /etc/systemd/system/media-player.service
```

Change `Environment=DISPLAY=:0` to your display number (e.g., `DISPLAY=:1`).

## Testing Auto-Start

To test if auto-start will work without rebooting:

```bash
# Stop services if running
sudo systemctl stop media-player.service
sudo systemctl stop gdrive-sync.service

# Start them again
sudo systemctl start gdrive-sync.service
sudo systemctl start media-player.service

# Check status
sudo systemctl status gdrive-sync.service
sudo systemctl status media-player.service
```

If both services show "active (running)", auto-start should work after reboot.

## Notes

- The services run as your user (not root) for security
- Logs are stored in systemd journal (use `journalctl` to view)
- Services auto-restart if they crash
- The media player waits for the graphical interface to be ready
- Google Drive sync waits for network to be available
- Both services use absolute paths, so they work from any directory

## Getting Help

If you continue to have issues:

1. Check the logs as shown above
2. Verify all prerequisites are met
3. Test running the scripts manually first
4. Check the main [README.md](../README.md) for general troubleshooting
