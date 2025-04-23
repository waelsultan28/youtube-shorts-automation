# --- YouTube Shorts Uploader ---
# Uploads videos to YouTube with optimized metadata

import os
import json
import colorama
from colorama import Fore, Style, Back
import traceback
import argparse

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

# Import the rest of the code from the original uploader.py
# ...

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
        
        # Your main code here
        # ...
        
        print(f"{Style.BRIGHT}{Fore.GREEN}----- Upload Process Finished -----{Style.RESET_ALL}")
        
    except Exception as e:
        print_fatal(f"Unexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
