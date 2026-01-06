#!/usr/bin/env python3
"""
Raspberry Pi 5 Media Player
Plays photos and videos with Ken Burns effect on photos
Designed for continuous loop playback
"""

import os
import sys
import time
import random
import logging
import yaml
import cv2
import numpy as np
import pygame
from pathlib import Path
from PIL import Image
import pillow_heif

class MediaPlayer:
    def __init__(self, config_path='config.yaml'):
        """Initialize the media player"""
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.media_files = []
        self.current_index = 0
        
        # Register HEIF opener with PIL
        pillow_heif.register_heif_opener()
        
        # Initialize pygame
        pygame.init()
        
        # Setup display
        self.setup_display()
        
        self.logger.info("Media player initialized")
    
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
        self.logger = logging.getLogger('MediaPlayer')
    
    def setup_display(self):
        """Setup pygame display"""
        player_config = self.config['media_player']
        
        if player_config['fullscreen']:
            # Get display info for fullscreen
            display_info = pygame.display.Info()
            self.screen_width = display_info.current_w
            self.screen_height = display_info.current_h
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.FULLSCREEN
            )
        else:
            # Use configured resolution or default
            resolution = player_config.get('resolution')
            if resolution:
                self.screen_width, self.screen_height = resolution
            else:
                self.screen_width, self.screen_height = 1920, 1080
            
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height)
            )
        
        pygame.display.set_caption("Raspberry Pi Media Player")
        pygame.mouse.set_visible(False)  # Hide mouse cursor
        
        self.logger.info(f"Display initialized: {self.screen_width}x{self.screen_height}")
    
    def scan_media_files(self):
        """Scan local media directory for supported files"""
        media_dir = self.config['google_drive']['local_media_dir']
        
        if not os.path.exists(media_dir):
            self.logger.warning(f"Media directory not found: {media_dir}")
            return []
        
        video_formats = [fmt.lower() for fmt in self.config['media_player']['video_formats']]
        image_formats = [fmt.lower() for fmt in self.config['media_player']['image_formats']]
        supported_formats = video_formats + image_formats
        
        media_files = []
        
        # Recursively scan for media files
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                ext = os.path.splitext(file.lower())[1]
                if ext in supported_formats:
                    file_path = os.path.join(root, file)
                    
                    # Determine media type
                    if ext in video_formats:
                        media_type = 'video'
                    else:
                        media_type = 'image'
                    
                    media_files.append({
                        'path': file_path,
                        'type': media_type,
                        'name': file
                    })
        
        self.logger.info(f"Found {len(media_files)} media files")
        return media_files
    
    def load_image(self, image_path):
        """Load an image file (including HEIC) and convert to numpy array"""
        try:
            # Use PIL to load image (supports HEIC via pillow_heif)
            pil_image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert PIL image to numpy array
            img_array = np.array(pil_image)
            
            # Convert RGB to BGR for OpenCV
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            return img_array
            
        except Exception as e:
            self.logger.error(f"Error loading image {image_path}: {e}")
            return None
    
    def resize_image(self, image, target_width, target_height):
        """Resize image to fit screen while maintaining aspect ratio"""
        height, width = image.shape[:2]
        
        # Calculate aspect ratios
        image_aspect = width / height
        screen_aspect = target_width / target_height
        
        if image_aspect > screen_aspect:
            # Image is wider, fit to width
            new_width = target_width
            new_height = int(target_width / image_aspect)
        else:
            # Image is taller, fit to height
            new_height = target_height
            new_width = int(target_height * image_aspect)
        
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        
        # Create black canvas and center image
        canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        y_offset = (target_height - new_height) // 2
        x_offset = (target_width - new_width) // 2
        canvas[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized
        
        return canvas
    
    def apply_ken_burns_effect(self, image, duration):
        """Apply Ken Burns pan and zoom effect to an image"""
        ken_burns_config = self.config['media_player']['ken_burns']
        max_zoom = ken_burns_config['max_zoom']
        steps = max(ken_burns_config['steps'], 1)  # Ensure steps is at least 1
        
        height, width = image.shape[:2]
        
        # Randomly choose zoom direction (zoom in or zoom out)
        zoom_in = random.choice([True, False])
        
        # Randomly choose pan direction
        start_x = random.uniform(0, 0.1)
        start_y = random.uniform(0, 0.1)
        end_x = random.uniform(0, 0.1)
        end_y = random.uniform(0, 0.1)
        
        # Calculate time per frame
        frame_delay = duration / steps
        target_fps = steps / duration
        
        clock = pygame.time.Clock()
        
        for step in range(steps):
            # Check for quit events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        return False
            
            # Calculate current zoom and pan
            progress = step / steps
            
            if zoom_in:
                current_zoom = 1.0 + (max_zoom - 1.0) * progress
            else:
                current_zoom = max_zoom - (max_zoom - 1.0) * progress
            
            # Interpolate pan position
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress
            
            # Calculate crop region
            crop_width = int(width / current_zoom)
            crop_height = int(height / current_zoom)
            
            # Apply pan offset
            x_offset = int(current_x * (width - crop_width))
            y_offset = int(current_y * (height - crop_height))
            
            # Ensure we don't go out of bounds
            x_offset = max(0, min(x_offset, width - crop_width))
            y_offset = max(0, min(y_offset, height - crop_height))
            
            # Crop and zoom
            cropped = image[y_offset:y_offset+crop_height, x_offset:x_offset+crop_width]
            zoomed = cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LINEAR)
            
            # Convert to pygame surface
            zoomed_rgb = cv2.cvtColor(zoomed, cv2.COLOR_BGR2RGB)
            surface = pygame.surfarray.make_surface(np.transpose(zoomed_rgb, (1, 0, 2)))
            
            # Display
            self.screen.fill((0, 0, 0))
            # Center the surface on screen
            x_pos = (self.screen_width - width) // 2
            y_pos = (self.screen_height - height) // 2
            self.screen.blit(surface, (x_pos, y_pos))
            pygame.display.flip()
            
            # Maintain frame rate
            clock.tick(target_fps)
        
        return True
    
    def play_image(self, image_path):
        """Play an image with Ken Burns effect"""
        self.logger.info(f"Playing image: {image_path}")
        
        # Load image
        image = self.load_image(image_path)
        if image is None:
            return True
        
        # Resize to screen
        image = self.resize_image(image, self.screen_width, self.screen_height)
        
        # Get photo duration
        duration = self.config['media_player']['photo_duration']
        
        # Apply Ken Burns effect if enabled
        if self.config['media_player']['ken_burns_effect']:
            return self.apply_ken_burns_effect(image, duration)
        else:
            # Simple static display
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            surface = pygame.surfarray.make_surface(np.transpose(image_rgb, (1, 0, 2)))
            
            self.screen.fill((0, 0, 0))
            self.screen.blit(surface, (0, 0))
            pygame.display.flip()
            
            # Wait for duration
            start_time = time.time()
            while time.time() - start_time < duration:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                            return False
                time.sleep(0.1)
            
            return True
    
    def play_video(self, video_path):
        """Play a video file"""
        self.logger.info(f"Playing video: {video_path}")
        
        try:
            # Open video with OpenCV
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                self.logger.error(f"Failed to open video: {video_path}")
                return True
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0:
                fps = 30  # Default to 30 fps if unknown
            
            frame_delay = 1.0 / fps
            clock = pygame.time.Clock()
            
            while True:
                # Check for quit events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        cap.release()
                        return False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                            cap.release()
                            return False
                
                # Read frame
                ret, frame = cap.read()
                
                if not ret:
                    # End of video
                    break
                
                # Resize frame to fit screen
                frame = self.resize_image(frame, self.screen_width, self.screen_height)
                
                # Convert to pygame surface
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                surface = pygame.surfarray.make_surface(np.transpose(frame_rgb, (1, 0, 2)))
                
                # Display
                self.screen.fill((0, 0, 0))
                self.screen.blit(surface, (0, 0))
                pygame.display.flip()
                
                # Maintain frame rate
                clock.tick(fps)
            
            cap.release()
            return True
            
        except Exception as e:
            self.logger.error(f"Error playing video {video_path}: {e}")
            return True
    
    def play_media(self, media_item):
        """Play a single media item"""
        if media_item['type'] == 'image':
            return self.play_image(media_item['path'])
        elif media_item['type'] == 'video':
            return self.play_video(media_item['path'])
        return True
    
    def run(self):
        """Main playback loop"""
        self.logger.info("Starting media player")
        
        running = True
        
        while running:
            # Scan for media files
            self.media_files = self.scan_media_files()
            
            if not self.media_files:
                self.logger.warning("No media files found. Waiting 30 seconds...")
                
                # Display message on screen
                font = pygame.font.Font(None, 48)
                text = font.render("No media files found. Waiting for sync...", True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                
                self.screen.fill((0, 0, 0))
                self.screen.blit(text, text_rect)
                pygame.display.flip()
                
                # Wait and check for quit
                for _ in range(300):  # 30 seconds in 0.1s increments
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            break
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                                running = False
                                break
                    if not running:
                        break
                    time.sleep(0.1)
                
                continue
            
            # Shuffle if configured
            if self.config['media_player']['shuffle']:
                random.shuffle(self.media_files)
            
            # Play all media files
            for media_item in self.media_files:
                if not self.play_media(media_item):
                    running = False
                    break
        
        # Cleanup
        pygame.quit()
        self.logger.info("Media player stopped")

def main():
    """Main entry point"""
    player = MediaPlayer()
    player.run()

if __name__ == "__main__":
    main()
