#!/usr/bin/env python3
"""
Google Drive Sync Script for Raspberry Pi Media Player
Syncs media files from a shared Google Drive folder to local storage
Runs continuously with configurable sync interval
"""

import os
import sys
import time
import logging
import yaml
from pathlib import Path
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from datetime import datetime

class GoogleDriveSync:
    def __init__(self, config_path='config.yaml'):
        """Initialize the Google Drive sync client"""
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.drive = None
        
    def load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_path}' not found.")
            print("Please copy config.yaml.example to config.yaml and update settings.")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            sys.exit(1)
    
    def setup_logging(self):
        """Configure logging"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'media_player.log')
        
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('GoogleDriveSync')
    
    def authenticate(self):
        """Authenticate with Google Drive using OAuth2"""
        try:
            client_secrets = self.config['google_drive']['client_secrets_file']
            
            if not os.path.exists(client_secrets):
                self.logger.error(f"Client secrets file not found: {client_secrets}")
                self.logger.error("Please download OAuth2 credentials from Google Cloud Console")
                return False
            
            # Create settings for PyDrive2
            settings = {
                "client_config_backend": "file",
                "client_config_file": client_secrets,
                "save_credentials": True,
                "save_credentials_backend": "file",
                "save_credentials_file": "credentials.json",
                "get_refresh_token": True,
                "oauth_scope": ["https://www.googleapis.com/auth/drive.readonly"]
            }
            
            gauth = GoogleAuth(settings=settings)
            
            # Try to load saved credentials
            gauth.LoadCredentialsFile("credentials.json")
            
            if gauth.credentials is None:
                # Authenticate if credentials don't exist
                self.logger.info("No saved credentials found. Starting OAuth2 flow...")
                gauth.LocalWebserverAuth()
            elif gauth.access_token_expired:
                # Refresh if expired
                self.logger.info("Access token expired. Refreshing...")
                gauth.Refresh()
            else:
                # Initialize with existing credentials
                gauth.Authorize()
            
            # Save credentials for next run
            gauth.SaveCredentialsFile("credentials.json")
            
            self.drive = GoogleDrive(gauth)
            self.logger.info("Successfully authenticated with Google Drive")
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    def get_folder_contents(self, folder_id, path=''):
        """Recursively get all files and folders from Google Drive"""
        try:
            # Query for all items in the folder
            query = f"'{folder_id}' in parents and trashed=false"
            file_list = self.drive.ListFile({'q': query}).GetList()
            
            items = []
            for item in file_list:
                item_info = {
                    'id': item['id'],
                    'title': item['title'],
                    'mimeType': item['mimeType'],
                    'path': os.path.join(path, item['title'])
                }
                
                # If it's a folder, recursively get its contents
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    item_info['is_folder'] = True
                    items.append(item_info)
                    # Recursively get folder contents
                    subfolder_items = self.get_folder_contents(
                        item['id'], 
                        os.path.join(path, item['title'])
                    )
                    items.extend(subfolder_items)
                else:
                    item_info['is_folder'] = False
                    items.append(item_info)
            
            return items
            
        except Exception as e:
            self.logger.error(f"Error getting folder contents: {e}")
            return []
    
    def is_media_file(self, filename):
        """Check if a file is a supported media file"""
        ext = os.path.splitext(filename.lower())[1]
        video_formats = self.config['media_player']['video_formats']
        image_formats = self.config['media_player']['image_formats']
        return ext in video_formats or ext in image_formats
    
    def sync_files(self):
        """Sync media files from Google Drive to local storage"""
        try:
            folder_id = self.config['google_drive']['folder_id']
            local_dir = self.config['google_drive']['local_media_dir']
            delete_local_when_removed = self.config['google_drive'].get('delete_local_when_removed', True)
            
            if folder_id == "YOUR_FOLDER_ID_HERE":
                self.logger.error("Please configure the Google Drive folder ID in config.yaml")
                return False
            
            self.logger.info(f"Starting sync from Google Drive folder: {folder_id}")
            
            # Create local media directory if it doesn't exist
            Path(local_dir).mkdir(parents=True, exist_ok=True)
            
            # Get all files from Google Drive
            items = self.get_folder_contents(folder_id)
            
            # Filter for media files only
            media_files = [item for item in items if not item['is_folder'] and self.is_media_file(item['title'])]
            
            self.logger.info(f"Found {len(media_files)} media files in Google Drive")
            
            # Track all Google Drive file paths for deletion check
            # Normalize to absolute paths for comparison
            gdrive_file_paths = set()
            for item in media_files:
                # Join local_dir with relative path, then resolve to absolute path
                gdrive_file_paths.add(str(Path(local_dir).joinpath(item['path']).resolve()))
            
            # Download or update files
            downloaded_count = 0
            skipped_count = 0
            
            for item in media_files:
                local_path = os.path.join(local_dir, item['path'])
                local_dir_path = os.path.dirname(local_path)
                
                # Create subdirectories as needed
                Path(local_dir_path).mkdir(parents=True, exist_ok=True)
                
                # Check if file already exists
                if os.path.exists(local_path):
                    # For simplicity, skip existing files
                    # In production, you might want to compare modification times or checksums
                    skipped_count += 1
                    continue
                
                try:
                    # Download file
                    self.logger.info(f"Downloading: {item['path']}")
                    file_obj = self.drive.CreateFile({'id': item['id']})
                    file_obj.GetContentFile(local_path)
                    downloaded_count += 1
                except Exception as e:
                    self.logger.error(f"Error downloading {item['path']}: {e}")
            
            # Delete local files that are no longer on Google Drive
            deleted_count = 0
            if delete_local_when_removed:
                deleted_count = self.delete_orphaned_files(local_dir, gdrive_file_paths)
            
            self.logger.info(f"Sync complete. Downloaded: {downloaded_count}, Skipped: {skipped_count}, Deleted: {deleted_count}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during sync: {e}")
            return False
    
    def delete_orphaned_files(self, local_dir, gdrive_file_paths):
        """Delete local files that no longer exist on Google Drive"""
        try:
            deleted_count = 0
            local_dir_path = Path(local_dir).resolve()
            
            self.logger.info("Checking for files to delete...")
            
            # Get all local media files
            local_files = []
            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Only consider media files
                    if self.is_media_file(file):
                        local_files.append(file_path)
            
            # Find files to delete (exist locally but not on Google Drive)
            for local_file in local_files:
                local_file_path = Path(local_file).resolve()
                
                # Safety check: ensure file is within local_media_dir
                try:
                    local_file_path.relative_to(local_dir_path)
                except ValueError:
                    self.logger.warning(f"Skipping file outside media directory: {local_file}")
                    continue
                
                # Check if file exists on Google Drive (compare resolved paths)
                if str(local_file_path) not in gdrive_file_paths:
                    try:
                        self.logger.info(f"Deleting local file (not in Drive): {os.path.relpath(local_file, local_dir)}")
                        os.remove(local_file)
                        deleted_count += 1
                    except Exception as e:
                        self.logger.error(f"Error deleting {local_file}: {e}")
            
            # Clean up empty directories
            self.cleanup_empty_directories(local_dir)
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error during orphaned file deletion: {e}")
            return 0
    
    def cleanup_empty_directories(self, local_dir):
        """Remove empty directories in the media directory"""
        try:
            local_dir_path = Path(local_dir).resolve()
            
            # Walk from bottom to top to handle nested directories
            for root, dirs, files in os.walk(local_dir, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    dir_path_obj = Path(dir_path).resolve()
                    
                    # Safety check: ensure directory is within local_media_dir
                    try:
                        dir_path_obj.relative_to(local_dir_path)
                    except ValueError:
                        continue
                    
                    # Check if directory exists and is empty
                    try:
                        if os.path.exists(dir_path) and not os.listdir(dir_path):
                            self.logger.info(f"Removing empty directory: {os.path.relpath(dir_path, local_dir)}")
                            os.rmdir(dir_path)
                    except FileNotFoundError:
                        # Directory was already removed, skip silently
                        pass
                    except Exception as e:
                        self.logger.error(f"Error removing directory {dir_path}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error during empty directory cleanup: {e}")
    
    def run(self):
        """Main run loop - sync files at configured interval"""
        if not self.authenticate():
            self.logger.error("Failed to authenticate. Exiting.")
            sys.exit(1)
        
        sync_interval = self.config['google_drive']['sync_interval'] * 60  # Convert to seconds
        
        self.logger.info(f"Starting sync service (interval: {self.config['google_drive']['sync_interval']} minutes)")
        
        while True:
            try:
                self.sync_files()
                self.logger.info(f"Next sync in {self.config['google_drive']['sync_interval']} minutes")
                time.sleep(sync_interval)
            except KeyboardInterrupt:
                self.logger.info("Sync service stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in sync loop: {e}")
                self.logger.info("Retrying in 60 seconds...")
                time.sleep(60)

def main():
    """Main entry point"""
    sync = GoogleDriveSync()
    sync.run()

if __name__ == "__main__":
    main()
