#!/usr/bin/env python3
"""
Test script to verify installation and configuration
Run this after installation to check if everything is set up correctly
"""

import sys
import os
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} not found: {filepath}")
        return False

def check_import(module_name):
    """Try to import a Python module"""
    try:
        __import__(module_name)
        print(f"✓ {module_name} is installed")
        return True
    except ImportError:
        print(f"✗ {module_name} is not installed")
        return False

def main():
    print("=" * 50)
    print("Raspberry Pi Media Player - Installation Check")
    print("=" * 50)
    print()
    
    all_ok = True
    
    # Check configuration files
    print("Checking configuration files...")
    all_ok &= check_file_exists("config.yaml", "Configuration file")
    all_ok &= check_file_exists("config.yaml.example", "Example configuration")
    all_ok &= check_file_exists("client_secrets.json.example", "Example OAuth2 credentials")
    
    if not check_file_exists("client_secrets.json", "OAuth2 credentials"):
        print("  → You need to download this from Google Cloud Console")
        all_ok = False
    
    print()
    
    # Check Python scripts
    print("Checking Python scripts...")
    all_ok &= check_file_exists("media_player.py", "Media player script")
    all_ok &= check_file_exists("gdrive_sync.py", "Google Drive sync script")
    print()
    
    # Check required Python modules
    print("Checking Python dependencies...")
    modules = [
        'pygame',
        'cv2',
        'numpy',
        'PIL',
        'pillow_heif',
        'pydrive2',
        'yaml',
        'google.auth',
    ]
    
    for module in modules:
        all_ok &= check_import(module)
    
    print()
    
    # Check media directory
    print("Checking directories...")
    media_dir = Path("media")
    if media_dir.exists():
        print(f"✓ Media directory exists: {media_dir}")
        media_count = len(list(media_dir.rglob("*.*")))
        print(f"  → Contains {media_count} files")
    else:
        print(f"✗ Media directory not found: {media_dir}")
        print("  → Will be created automatically on first sync")
    
    print()
    
    # Check configuration content
    print("Checking configuration...")
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        folder_id = config['google_drive']['folder_id']
        if folder_id == "YOUR_FOLDER_ID_HERE":
            print("✗ Google Drive folder ID not configured")
            print("  → Edit config.yaml and set your folder ID")
            all_ok = False
        else:
            print(f"✓ Google Drive folder ID configured: {folder_id}")
        
    except Exception as e:
        print(f"✗ Error reading config.yaml: {e}")
        all_ok = False
    
    print()
    print("=" * 50)
    
    if all_ok:
        print("✓ All checks passed! You're ready to run the media player.")
        print()
        print("Next steps:")
        print("1. Start Google Drive sync: python3 gdrive_sync.py")
        print("2. Start media player: python3 media_player.py")
    else:
        print("✗ Some checks failed. Please review the errors above.")
        print()
        print("Common fixes:")
        print("1. Run install.sh if you haven't already")
        print("2. Activate virtual environment: source venv/bin/activate")
        print("3. Copy config.yaml.example to config.yaml")
        print("4. Download client_secrets.json from Google Cloud Console")
        print("5. Edit config.yaml with your Google Drive folder ID")
    
    print("=" * 50)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
