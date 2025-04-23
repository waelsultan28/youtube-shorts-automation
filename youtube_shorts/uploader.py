# --- YouTube Shorts Uploader ---
# Uploads videos to YouTube with optimized metadata

import os
import json
import colorama
from colorama import Fore, Style, Back
import traceback
import argparse
import openpyxl
import time
import re
from datetime import datetime, timedelta
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Initialize colorama
colorama.init(autoreset=True)

# --- Print Helper Functions ---
def print_info(msg, indent=0): prefix = "  " * indent; print(f"{prefix}{Fore.BLUE}i INFO:{Style.RESET_ALL} {msg}")
def print_success(msg, indent=0): prefix = "  " * indent; print(f"{prefix}{Fore.GREEN}✓ SUCCESS:{Style.RESET_ALL} {msg}")
def print_warning(msg, indent=0): prefix = "  " * indent; print(f"{prefix}{Fore.YELLOW}! WARNING:{Style.RESET_ALL} {msg}")
def print_error(msg, indent=0, include_traceback=False):
    prefix = "  " * indent
    print(f"{prefix}{Fore.RED}✗ ERROR:{Style.RESET_ALL} {msg}")
    if include_traceback:
        traceback.print_exc()
def print_fatal(msg, indent=0): prefix = "  " * indent; print(f"{prefix}{Back.RED}{Fore.WHITE}{Style.BRIGHT} FATAL: {msg} {Style.RESET_ALL}"); exit(1)

# --- Constants ---
EXCEL_FILENAME = "shorts_data.xlsx"
DOWNLOADED_SHEET_NAME = "Downloaded"
UPLOADED_SHEET_NAME = "Uploaded"
CONFIG_FILENAME = "config.txt"
DOWNLOADS_FOLDER_NAME = "shorts_downloads"
METADATA_FOLDER_NAME = "shorts_metadata"

# --- Uploader Functions ---
def load_config():
    """Loads configuration from config.txt file."""
    config = {}
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', CONFIG_FILENAME)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        return config
    except Exception as e:
        print_error(f"Error loading config: {e}")
        return {}

def setup_browser(config):
    """Sets up the browser for uploading."""
    try:
        # Set up Firefox options
        options = webdriver.FirefoxOptions()
        
        # Set up profile if specified
        profile_path = config.get('PROFILE_PATH')
        if profile_path:
            print_info(f"Using Firefox profile: {profile_path}")
            options.add_argument(f"-profile {profile_path}")
        
        # Create browser instance
        driver = webdriver.Firefox(options=options)
        driver.maximize_window()
        return driver
    except Exception as e:
        print_error(f"Error setting up browser: {e}", include_traceback=True)
        return None

def get_videos_to_upload(max_uploads=None):
    """Gets a list of videos to upload from the Excel file."""
    videos = []
    excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', EXCEL_FILENAME)
    
    try:
        # Check if Excel file exists
        if not os.path.exists(excel_path):
            print_error(f"Excel file not found: {excel_path}")
            return []
        
        # Load workbook and sheets
        workbook = openpyxl.load_workbook(excel_path)
        
        # Check if sheets exist
        if DOWNLOADED_SHEET_NAME not in workbook.sheetnames:
            print_error(f"Sheet '{DOWNLOADED_SHEET_NAME}' not found in Excel file")
            return []
        if UPLOADED_SHEET_NAME not in workbook.sheetnames:
            print_error(f"Sheet '{UPLOADED_SHEET_NAME}' not found in Excel file")
            return []
        
        downloaded_sheet = workbook[DOWNLOADED_SHEET_NAME]
        uploaded_sheet = workbook[UPLOADED_SHEET_NAME]
        
        # Get list of already uploaded video IDs
        uploaded_ids = set()
        for row in uploaded_sheet.iter_rows(min_row=2, values_only=True):
            if row and row[0]:  # Video Index column
                uploaded_ids.add(row[0])
        
        # Get videos to upload from downloaded sheet
        for row in downloaded_sheet.iter_rows(min_row=2, values_only=True):
            if not row or not row[0]:  # Skip empty rows
                continue
            
            video_id = row[0]  # Video Index column
            if video_id in uploaded_ids:  # Skip already uploaded videos
                continue
            
            # Check if video file exists
            video_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', DOWNLOADS_FOLDER_NAME, f"{video_id}.mp4")
            if not os.path.exists(video_file):
                print_warning(f"Video file not found: {video_file}")
                continue
            
            # Check if metadata file exists
            metadata_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', METADATA_FOLDER_NAME, f"{video_id}.json")
            if not os.path.exists(metadata_file):
                print_warning(f"Metadata file not found: {metadata_file}")
                continue
            
            # Load metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Add video to list
            videos.append({
                'video_id': video_id,
                'video_file': video_file,
                'metadata': metadata
            })
            
            # Limit number of videos if specified
            if max_uploads and len(videos) >= max_uploads:
                break
        
        return videos
    except Exception as e:
        print_error(f"Error getting videos to upload: {e}", include_traceback=True)
        return []

# --- Main Function ---
def main():
    """Main function to run the uploader."""
    try:
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="YouTube Shorts Uploader")
        parser.add_argument("--analyze", "-a", action="store_true", help="Analyze upload performance and suggest improvements")
        parser.add_argument("--max-uploads", "-m", type=int, help="Maximum number of videos to upload")
        args = parser.parse_args()
        
        # Initialize colorama
        colorama.init(autoreset=True)
        
        print(f"{Fore.CYAN}--- YouTube Shorts Uploader ---{Style.RESET_ALL}")
        
        # If analyze flag is set, run analysis and exit
        if args.analyze:
            print_info("Running upload performance analysis...")
            print_info("Analysis feature is not implemented in the package module.")
            print_info("Please use the original uploader.py script for analysis.")
            return
        
        # Load configuration
        print_info("Loading configuration...")
        config = load_config()
        if not config:
            print_fatal("Failed to load configuration. Cannot proceed.")
            return
        
        # Get max uploads from args or config
        max_uploads = args.max_uploads
        if not max_uploads and 'MAX_UPLOADS' in config:
            try:
                max_uploads = int(config['MAX_UPLOADS'])
            except ValueError:
                print_warning(f"Invalid MAX_UPLOADS value in config: {config['MAX_UPLOADS']}. Using default.")
                max_uploads = 5
        
        # Get videos to upload
        print_info(f"Getting videos to upload (max: {max_uploads})...")
        videos = get_videos_to_upload(max_uploads)
        if not videos:
            print_warning("No videos found to upload.")
            return
        
        print_info(f"Found {len(videos)} videos to upload.")
        print_info("This is a package module. For full functionality, use the original uploader.py script.")
        print_info("Or import this module and call specific functions as needed.")
        
        print(f"\n{Style.BRIGHT}{Fore.GREEN}----- Upload Process Finished -----{Style.RESET_ALL}")
        
    except Exception as e:
        print_fatal(f"Unexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
