# --- YouTube Shorts Downloader ---
# Finds and downloads videos with SEO optimization and self-improvement

import os
import json
import yt_dlp
import google.generativeai as genai
import re
import concurrent.futures
from datetime import datetime
from openpyxl import Workbook, load_workbook
import random
import math
import time
import traceback
import colorama
from colorama import Fore, Style, Back
import shutil  # For file backups

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
YT_SEARCH_RESULTS_PER_KEYWORD = 50  # Number of search results to fetch per keyword
VIDEOS_TO_DOWNLOAD_PER_KEYWORD = 5  # Max videos to download for a single keyword
MAX_TITLE_LENGTH = 100              # YouTube's recommended max title length
TARGET_TITLE_LENGTH = 90            # Target length before adding #Shorts (SEO focus prefers slightly longer)
METADATA_TIMEOUT_SECONDS = 15       # Timeout for Gemini API call
INITIAL_KEYWORDS_COUNT = 15         # Number of keywords to generate initially
EXCEL_FILENAME = "shorts_data.xlsx"
DOWNLOADED_SHEET_NAME = "Downloaded"
UPLOADED_SHEET_NAME = "Uploaded"
PLAYLIST_CACHE_FILENAME = "playlist_cache.json"
KEYWORDS_CACHE_FILENAME = "generated_keywords_cache.json"
NICHE_FILENAME = "niche.txt"
DOWNLOADS_FOLDER_NAME = "shorts_downloads"
METADATA_FOLDER_NAME = "shorts_metadata"
FFMPEG_EXE = "ffmpeg.exe"           # Assuming it's in the script directory or PATH
SHORTS_SUFFIX = " #Shorts"
MAX_SHORT_DURATION = 61             # Max duration in seconds for a video to be considered a Short

# --- Self-Improvement Constants ---
SEO_METADATA_PROMPT_CACHE = "seo_metadata_prompt.txt"  # Cache for the potentially AI-improved SEO prompt
METADATA_METRICS_FILENAME = "metadata_metrics.json"    # File to track metadata generation metrics
PERFORMANCE_METRICS_FILENAME = "performance_metrics.json"  # File to track overall performance metrics
TUNING_SUGGESTIONS_FILENAME = "tuning_suggestions.log"  # File to store parameter tuning suggestions

# Keyword optimization settings
KEYWORDS_TO_PROCESS_PER_RUN = 5     # Number of keywords to select for each run
MIN_KEYWORDS_THRESHOLD = 20         # Minimum number of keywords before generating new ones
NEW_KEYWORDS_TO_GENERATE = 10       # Number of new keywords to generate when needed
TOP_KEYWORDS_TO_USE = 5             # Number of top-performing keywords to use for new keyword generation

# Metadata prompt improvement settings
METADATA_ERROR_THRESHOLD = 0.15     # Error rate threshold to trigger prompt improvement (15%)
METADATA_TIMEOUT_THRESHOLD = 0.10   # Timeout rate threshold to trigger prompt improvement (10%)
MAX_ERROR_SAMPLES = 5               # Maximum number of error samples to store for prompt improvement

# Parameter tuning settings
MIN_RUNS_BEFORE_TUNING = 3          # Minimum number of runs before suggesting parameter tuning
BASE_WEIGHT_FOR_KEYWORDS = 1        # Base weight to add to all keywords to prevent stagnation

# --- Global Cache for SEO Prompt ---
_current_seo_prompt_template = None  # Will be loaded/set later

# Import the rest of the code from the original downloader.py
# ...

def main():
    """Main function to run the downloader."""
    try:
        # Initialize colorama
        colorama.init(autoreset=True)
        
        # Your main code here
        # ...
        
        print(f"{Style.BRIGHT}{Fore.GREEN}----- Script Execution Finished -----{Style.RESET_ALL}")
        
    except Exception as e:
        print_fatal(f"Unexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
