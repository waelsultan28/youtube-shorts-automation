#!/usr/bin/env python3
"""
Setup script to initialize the working directory for YouTube Shorts Automation.
This script creates the necessary folders and configuration files.
"""

import os
import shutil
import sys
import openpyxl
from openpyxl import Workbook
import json
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init(autoreset=True)

def print_info(msg): print(f"{Fore.BLUE}INFO:{Style.RESET_ALL} {msg}")
def print_success(msg): print(f"{Fore.GREEN}SUCCESS:{Style.RESET_ALL} {msg}")
def print_warning(msg): print(f"{Fore.YELLOW}WARNING:{Style.RESET_ALL} {msg}")
def print_error(msg): print(f"{Fore.RED}ERROR:{Style.RESET_ALL} {msg}")

def setup_workspace(target_dir=None):
    """
    Set up the working directory with necessary folders and files.
    
    Args:
        target_dir: The target directory to set up. If None, uses the current directory.
    """
    # Determine target directory
    if target_dir is None:
        target_dir = os.getcwd()
    
    print_info(f"Setting up workspace in: {target_dir}")
    
    # Create directories
    directories = [
        "shorts_downloads",
        "shorts_metadata"
    ]
    
    for directory in directories:
        dir_path = os.path.join(target_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print_success(f"Created directory: {directory}")
        else:
            print_info(f"Directory already exists: {directory}")
    
    # Copy template files
    template_files = {
        "config.txt.template": "config.txt",
        "niche.txt.template": "niche.txt"
    }
    
    package_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(package_dir, "data")
    
    for template, target in template_files.items():
        template_path = os.path.join(data_dir, template)
        target_path = os.path.join(target_dir, target)
        
        if not os.path.exists(target_path):
            if os.path.exists(template_path):
                shutil.copy2(template_path, target_path)
                print_success(f"Created file: {target}")
            else:
                print_error(f"Template file not found: {template}")
        else:
            print_info(f"File already exists: {target}")
    
    # Create Excel file if it doesn't exist
    excel_path = os.path.join(target_dir, "shorts_data.xlsx")
    if not os.path.exists(excel_path):
        wb = Workbook()
        
        # Set up Downloaded sheet
        downloaded_sheet = wb.active
        downloaded_sheet.title = "Downloaded"
        downloaded_sheet.append(["Video Index", "Optimized Title", "Downloaded Date", "Views", "Uploader", "Original Title"])
        
        # Set up Uploaded sheet
        uploaded_sheet = wb.create_sheet(title="Uploaded")
        uploaded_sheet.append(["Video Index", "Optimized Title", "YouTube Video ID", "Upload Timestamp", "Scheduled Time", "Publish Status"])
        
        # Save the workbook
        wb.save(excel_path)
        print_success(f"Created Excel file: shorts_data.xlsx")
    else:
        print_info(f"Excel file already exists: shorts_data.xlsx")
    
    # Create empty metrics files if they don't exist
    metrics_files = {
        "metadata_metrics.json": {
            "total_api_calls": 0,
            "parse_failures": 0,
            "timeouts": 0,
            "empty_title_errors": 0,
            "empty_description_errors": 0,
            "empty_tags_errors": 0,
            "last_run_date": "",
            "error_samples": []
        },
        "performance_metrics.json": {
            "total_shorts_found": 0,
            "total_suitable_shorts": 0,
            "total_downloads_attempted": 0,
            "total_successful_downloads": 0,
            "total_metadata_api_calls": 0,
            "total_metadata_errors": 0,
            "total_download_errors": 0,
            "keyword_performance": {},
            "runs": []
        }
    }
    
    for filename, default_content in metrics_files.items():
        file_path = os.path.join(target_dir, filename)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_content, f, indent=4)
            print_success(f"Created metrics file: {filename}")
        else:
            print_info(f"Metrics file already exists: {filename}")
    
    print_success("Workspace setup complete!")
    print_info("Next steps:")
    print_info("1. Edit config.txt to add your API keys and customize settings")
    print_info("2. Edit niche.txt to set your target niche")
    print_info("3. Run the scripts:")
    print_info("   - python -m youtube_shorts.performance_tracker")
    print_info("   - python -m youtube_shorts.downloader")
    print_info("   - python -m youtube_shorts.uploader")
    print_info("   Or use the command-line tools if installed as a package:")
    print_info("   - yt-track")
    print_info("   - yt-download")
    print_info("   - yt-upload")

def main():
    """Main function to run the setup script."""
    # Get target directory from command line arguments
    target_dir = None
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    
    setup_workspace(target_dir)

if __name__ == "__main__":
    main()
