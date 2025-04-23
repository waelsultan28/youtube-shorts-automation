# --- YouTube Shorts Performance Tracker ---
# Tracks performance metrics for uploaded YouTube Shorts

import os
import json
import colorama
from colorama import Fore, Style, Back
import traceback

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
UPLOADED_SHEET_NAME = "Uploaded"
API_CREDENTIALS_FILE = "client_secrets.json"
TOKEN_PICKLE_FILE = "token.pickle"

# Import the rest of the code from the original performance_tracker.py
# ...

def main():
    """Main function to run the performance tracker."""
    try:
        # Initialize colorama
        colorama.init(autoreset=True)
        
        # Your main code here
        # ...
        
        print(f"{Style.BRIGHT}{Fore.GREEN}----- Performance Tracking Finished -----{Style.RESET_ALL}")
        
    except Exception as e:
        print_fatal(f"Unexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
