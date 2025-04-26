# -*- coding: utf-8 -*-
import os
import json
import yt_dlp
import google.generativeai as genai
import re
import time
import concurrent.futures
# No timedelta needed for permanent cache
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
import traceback # Import traceback

# --- Constants ---
# File/Folder Names
CONFIG_FILENAME = "config.txt"
CHANNELS_FILENAME = "channels.txt"
DOWNLOADS_FOLDER_NAME = "shorts_downloads"
METADATA_FOLDER_NAME = "shorts_metadata"
EXCEL_FILENAME = "shorts_data.xlsx"
ERROR_LOG_FILENAME = "download_error_log.txt"
CHANNEL_PROCESSED_IDS_CACHE_FILENAME = "channel_processed_ids_cache.json" # Cache for processed video IDs {channel_url: [ids]}
CHANNEL_LISTING_CACHE_FILENAME = "channel_listing_cache.json" # Cache for fetched channel video lists {channel_url: [entries]} (permanent)
FFMPEG_EXE = "ffmpeg.exe"

# Excel Sheet Names / Headers / Indices
DOWNLOADED_SHEET_NAME = "Downloaded"
UPLOADED_SHEET_NAME = "Uploaded"
EXPECTED_DOWNLOADED_HEADERS = ["Video Index", "Optimized Title", "Downloaded Date", "Views", "Uploader", "Original Title"]
EXPECTED_UPLOADED_HEADERS = ["Video Index", "Optimized Title", "Upload Timestamp", "Scheduled Time", "Publish Status"]
ORIGINAL_TITLE_COL_IDX = 6 # Column F (1-based)
UPLOADER_COL_IDX = 5       # Column E (1-based)

# yt-dlp Settings
YT_PLAYLIST_FETCH_LIMIT = 50 # How many videos to initially check per channel (if not cached)
MAX_SHORT_DURATION = 61 # Max video duration in seconds (inclusive) - Currently unused, but defined

# Gemini Settings
METADATA_TIMEOUT_SECONDS = 30
DEFAULT_UPLOADER_NAME = "Unknown Uploader"

# --- End Constants ---

# --- Global Path Definitions ---
script_directory = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_directory, CONFIG_FILENAME)
channels_file_path = os.path.join(script_directory, CHANNELS_FILENAME)
download_folder = os.path.join(script_directory, DOWNLOADS_FOLDER_NAME)
metadata_folder = os.path.join(script_directory, METADATA_FOLDER_NAME)
excel_file = os.path.join(script_directory, EXCEL_FILENAME)
ERROR_LOG_FILE = os.path.join(script_directory, ERROR_LOG_FILENAME)
channel_processed_ids_cache_file = os.path.join(script_directory, CHANNEL_PROCESSED_IDS_CACHE_FILENAME)
channel_listing_cache_file = os.path.join(script_directory, CHANNEL_LISTING_CACHE_FILENAME) # Uses constant
ffmpeg_path = os.path.join(script_directory, FFMPEG_EXE)

# --- Logging Function ---
def log_error(message: str):
    """Logs an error message to the download error log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"CRITICAL: Failed write to log '{ERROR_LOG_FILE}': {e}\nOriginal: [{timestamp}] {message}")

# --- Configuration Loading ---
config = {}
try:
    with open(config_file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
except FileNotFoundError:
    log_error(f"FATAL: Config file '{config_file_path}' not found.")
    raise FileNotFoundError(f"FATAL: Configuration file '{config_file_path}' not found.")
except Exception as e:
    log_error(f"FATAL: Error reading config '{config_file_path}': {e}")
    raise Exception(f"FATAL: Error reading configuration file '{config_file_path}'.")

# --- Get Configurable Settings ---
API_KEY = config.get("API_KEY")
if not API_KEY:
    log_error("FATAL: API_KEY not found in 'config.txt'.")
    raise ValueError("FATAL: API_KEY missing or empty in config.txt.")

_DEFAULT_MAX_DOWNLOADS = 24
try:
    max_downloads_str = config.get("MAX_DOWNLOADS")
    max_downloads = int(max_downloads_str) if max_downloads_str else _DEFAULT_MAX_DOWNLOADS
    if max_downloads <= 0:
        print(f"Warning: MAX_DOWNLOADS invalid. Using default: {_DEFAULT_MAX_DOWNLOADS}")
        log_error(f"Warning: MAX_DOWNLOADS ('{max_downloads_str}') <= 0. Using default {_DEFAULT_MAX_DOWNLOADS}.")
        max_downloads = _DEFAULT_MAX_DOWNLOADS
except (ValueError, TypeError):
    print(f"Warning: Invalid MAX_DOWNLOADS. Using default: {_DEFAULT_MAX_DOWNLOADS}")
    log_error(f"Warning: Invalid MAX_DOWNLOADS ('{config.get('MAX_DOWNLOADS')}'). Using default {_DEFAULT_MAX_DOWNLOADS}.")
    max_downloads = _DEFAULT_MAX_DOWNLOADS

# SEO Config
seo_channel_name = config.get("SEO_CHANNEL_NAME", "Our Awesome Channel")
seo_channel_topic = config.get("SEO_CHANNEL_TOPIC", "interesting videos")
seo_example_tags_raw = config.get("SEO_EXAMPLE_TAGS", "tag1, tag2, youtube, video, shorts")
seo_example_tags = [tag.strip() for tag in seo_example_tags_raw.split(',') if tag.strip()]
seo_example_hashtags_raw = config.get("SEO_EXAMPLE_HASHTAGS", "#shorts #video #youtube")
seo_example_hashtags = [ht.strip() for ht in seo_example_hashtags_raw.split() if ht.strip().startswith('#')]

print(f"Settings: Max Downloads={max_downloads}, SEO Channel='{seo_channel_name}', Topic='{seo_channel_topic}'")

# Configure Gemini API
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
     log_error(f"FATAL: Failed Gemini config: {e}")
     raise Exception(f"FATAL: Failed to configure Gemini API: {e}")

# --- Function Definitions ---

def generate_seo_metadata(video_topic, channel_name, channel_topic, example_tags, example_hashtags, uploader_name=DEFAULT_UPLOADER_NAME):
    """Generates SEO-optimized metadata using Gemini API, including uploader credit."""
    example_tags_str = ", ".join(example_tags)
    example_hashtags_str = " ".join(example_hashtags)
    # Updated prompt to include uploader_name placeholder
    prompt = f"""
    do not include any explanation or any other text. just give me the metadata in below format.
    only apply the below format. do not include any other text or explanation.
    Generate SEO-optimized metadata for a YouTube Shorts video in the following structured format:
    You are a YOUTUBE SEO EXPERT A GURU one in million. you have insight knowledge of youtube shorts.
    you know how the ranking algorithm works and how to get more views and engagement.
    you know how creator like mrbeast, tseries, and other top creators get more views and engagement.
    your master of youtube shorts. you have worked with big creator know all secrets of youtube shorts.
    you have worked in google youtube team and you know all secrets of youtube shorts.
    Our Channel Name is "{channel_name}" and we are a channel about {channel_topic}.
    include a copyright fair use disclaimer in the description.
    APPLY ALL OF THE ABOVE KNOWLEDGE AND SECRETS TO BELOW metadata.

    <metadata>
        <title>
            Create an engaging, fast-paced, and action-driven title (max 100 chars incl. #Shorts) with a high CTR based on the video topic: '{video_topic}'.
            Use keywords for '{channel_topic}'. Use relevant emojis (🔥, 💪, 👀), numbers, power words (BEST, HOT, ULTIMATE, SECRET, TRY THIS). Add "#Shorts" at the end.
        </title>
        <description>
            Write an SEO-optimized description (max 4500 chars):
                * Start with the optimized video title.
                * 2-3 sentence engaging summary about '{video_topic}' and '{channel_topic}', using keywords/LSI naturally.
                * **Include credit: "Credit: {uploader_name}"** <-- UPLOADER CREDIT HERE
                * Include copyright disclaimer:
                  --------------【Copyright Disclaimer】-------------
                  All the videos, songs, images, and graphics used in the video belong to
                  their respective owners and I or this channel "{channel_name}" does not claim any right over them.
                  Copyright Disclaimer under section 107 of the Copyright Act of 1976, allowance is made for “fair use” for purposes such as criticism, comment, news reporting, teaching, scholarship, education and research. Fair use is a use permitted by copyright statute that might otherwise be infringing.
                * After disclaimer, add 10-15 relevant hashtags (inspired by: {example_hashtags_str}).
                * Add heading "Tags Used in Video :-" and list all tags from <tags> section below, comma-separated.
                * End with a Call to Action (e.g., "👍 Like & Subscribe to {channel_name}!").
                * Add heading "Ignored Hashtags :-" followed by a diverse list of relevant hashtags.
        </description>
        <tags>
            Suggest 15-25 SEO-friendly tags (comma-separated, max 500 chars total).
            * Start with keywords for '{video_topic}'. Include tags for '{channel_topic}' and channel name '{channel_name}'.
            * Use mix of general/specific tags. Inspire from: {example_tags_str}
        </tags>
    </metadata>

    **Video Topic**: {video_topic}
    """
    # Default includes credit
    default_metadata = { "title": f"{video_topic[:80]} #Shorts", "description": f"Desc: {video_topic}.\n\nCredit: {uploader_name}\n\n[Disclaimer]", "tags": ["default"] }
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        raw_text = ""
        try: raw_text = "".join(part.text for part in response.parts)
        except Exception: raw_text = response.text # Fallback
        if not raw_text: log_error(f"Gemini response empty for '{video_topic}'."); return default_metadata

        title_match = re.search(r"<title>(.*?)</title>", raw_text, re.DOTALL | re.IGNORECASE)
        desc_match = re.search(r"<description>(.*?)</description>", raw_text, re.DOTALL | re.IGNORECASE)
        tags_match = re.search(r"<tags>(.*?)</tags>", raw_text, re.DOTALL | re.IGNORECASE)
        metadata = {}
        # Title processing
        if title_match:
            metadata["title"] = title_match.group(1).strip()
            metadata["title"] = metadata["title"][:90].strip() # Limit length before adding #Shorts
            if not metadata["title"].lower().endswith("#shorts"): metadata["title"] += " #Shorts"
        else: metadata["title"] = default_metadata["title"]
        # Description processing
        if desc_match:
            metadata["description"] = desc_match.group(1).strip()
            credit_line = f"Credit: {uploader_name}"
            if credit_line not in metadata["description"]: metadata["description"] += f"\n\n{credit_line}" # Ensure credit
        else: metadata["description"] = default_metadata["description"]
        # Tags processing
        if tags_match:
            tags_raw = tags_match.group(1).strip()
            all_tags = [tag.strip() for tag in tags_raw.split(',') if tag.strip()]
            current_len = 0; final_tags = []
            for tag in all_tags:
                tag_len_with_comma = len(tag) + (1 if final_tags else 0)
                if current_len + tag_len_with_comma <= 495: final_tags.append(tag); current_len += tag_len_with_comma
                else: break # Stop if limit exceeded
            metadata["tags"] = final_tags
        else: metadata["tags"] = default_metadata["tags"]
        # Basic validation
        return metadata if metadata.get("title") and metadata.get("description") else default_metadata
    except Exception as e:
        log_error(f"Error in generate_seo_metadata for '{video_topic}': {e}")
        return default_metadata


def generate_metadata_with_timeout(video_topic, channel_name, channel_topic, example_tags, example_hashtags, uploader_name, timeout=METADATA_TIMEOUT_SECONDS):
    """Generates metadata with a timeout, passing required parameters."""
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(generate_seo_metadata, video_topic, channel_name, channel_topic, example_tags, example_hashtags, uploader_name)
            return future.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        log_error(f"Metadata timeout {timeout}s: {video_topic}.")
        return { "title": f"{video_topic[:80]} #Shorts", "description": f"Desc: {video_topic}.\n\nCredit: {uploader_name}\n\n[Disclaimer] Timeout.", "tags": ["timeout"] }
    except Exception as e:
         log_error(f"Metadata thread error: {video_topic}: {e}")
         return { "title": f"{video_topic[:80]} #Shorts", "description": f"Desc: {video_topic}.\n\nCredit: {uploader_name}\n\n[Disclaimer] Error.", "tags": ["error"] }


def create_folders():
    """Creates necessary folders if they don't exist."""
    for folder in [download_folder, metadata_folder]:
        try: os.makedirs(folder, exist_ok=True)
        except OSError as e: log_error(f"FATAL: Error creating folder '{folder}': {e}"); raise


def load_or_create_excel():
    """Loads Excel, checks/creates sheets, corrects headers, loads previous videos."""
    previously_downloaded_videos = set()
    wb = None; downloaded_sheet = None; uploaded_sheet = None # Initialize
    save_needed = False # Flag to save only if changes were made

    if not os.path.exists(excel_file):
        print(f"Excel file not found '{excel_file}'. Creating.")
        wb = Workbook(); save_needed = True
        downloaded_sheet = wb.active; downloaded_sheet.title = DOWNLOADED_SHEET_NAME
        downloaded_sheet.append(EXPECTED_DOWNLOADED_HEADERS)
        uploaded_sheet = wb.create_sheet(title=UPLOADED_SHEET_NAME)
        uploaded_sheet.append(EXPECTED_UPLOADED_HEADERS)
    else:
        print(f"Loading existing Excel: {excel_file}")
        try:
            wb = load_workbook(excel_file)
            # Check/Correct Downloaded Sheet
            if DOWNLOADED_SHEET_NAME not in wb.sheetnames:
                log_error(f"Sheet '{DOWNLOADED_SHEET_NAME}' missing. Creating."); downloaded_sheet = wb.create_sheet(DOWNLOADED_SHEET_NAME, 0); downloaded_sheet.append(EXPECTED_DOWNLOADED_HEADERS); save_needed = True
            else:
                downloaded_sheet = wb[DOWNLOADED_SHEET_NAME]; current_headers = [str(c.value) if c.value is not None else '' for c in downloaded_sheet[1]]
                if tuple(current_headers) != tuple(EXPECTED_DOWNLOADED_HEADERS):
                    log_error(f"Correcting headers in '{DOWNLOADED_SHEET_NAME}'."); print(f"Warning: Correcting headers in '{DOWNLOADED_SHEET_NAME}'.")
                    for i, h in enumerate(EXPECTED_DOWNLOADED_HEADERS): downloaded_sheet.cell(1, i + 1, h); save_needed = True
            # Check/Correct Uploaded Sheet
            if UPLOADED_SHEET_NAME not in wb.sheetnames:
                log_error(f"Sheet '{UPLOADED_SHEET_NAME}' missing. Creating."); uploaded_sheet = wb.create_sheet(UPLOADED_SHEET_NAME); uploaded_sheet.append(EXPECTED_UPLOADED_HEADERS); save_needed = True
            else:
                uploaded_sheet = wb[UPLOADED_SHEET_NAME]; current_headers = [str(c.value) if c.value is not None else '' for c in uploaded_sheet[1]]
                if tuple(current_headers) != tuple(EXPECTED_UPLOADED_HEADERS):
                    log_error(f"Correcting headers in '{UPLOADED_SHEET_NAME}'."); print(f"Warning: Correcting headers in '{UPLOADED_SHEET_NAME}'.")
                    for i, h in enumerate(EXPECTED_UPLOADED_HEADERS): uploaded_sheet.cell(1, i + 1, h); save_needed = True

            # Load previous videos (only if downloaded_sheet is valid)
            if downloaded_sheet:
                print("Loading previous Title/Uploader pairs...")
                max_col = max(ORIGINAL_TITLE_COL_IDX, UPLOADER_COL_IDX)
                for row in downloaded_sheet.iter_rows(min_row=2, max_col=max_col, values_only=True):
                    if len(row) >= max_col:
                        title, uploader = row[ORIGINAL_TITLE_COL_IDX - 1], row[UPLOADER_COL_IDX - 1]
                        if isinstance(title, str) and title.strip() and isinstance(uploader, str) and uploader.strip():
                             previously_downloaded_videos.add((title.strip(), uploader.strip()))
                print(f"Loaded {len(previously_downloaded_videos)} previous Title/Uploader pairs.")
            else: log_error("Could not load previous videos: Downloaded sheet object invalid.")

            print("Excel loaded.")
        except Exception as e:
            log_error(f"FATAL: Error loading/validating Excel '{excel_file}': {e}"); traceback.print_exc(); raise

    # Save workbook only if changes were made during loading/creation/correction
    if save_needed:
        try:
            wb.save(excel_file)
            print(f"Saved structural changes to Excel file: {excel_file}")
        except Exception as e:
            log_error(f"Error saving structural changes to Excel: {e}")
            print(f"Error saving structural changes to Excel: {e}")

    return wb, downloaded_sheet, uploaded_sheet, previously_downloaded_videos


def get_last_video_index(downloaded_sheet: Worksheet) -> int:
    """Gets the next video index based on the 'Downloaded' sheet."""
    max_index = 0
    if not downloaded_sheet: log_error("Cannot get last video index: Sheet is None."); return 1
    try:
        for row in downloaded_sheet.iter_rows(min_row=2, max_col=1, values_only=True):
            if row and row[0] and isinstance(row[0], str) and row[0].lower().startswith("video"):
                try: max_index = max(max_index, int(row[0][len("video"):]))
                except (ValueError, IndexError): pass # Ignore parsing errors
    except Exception as e: log_error(f"Error get_last_video_index: {e}"); return 1
    next_index = max_index + 1; print(f"Next video index: {next_index}"); return next_index


def load_channels() -> list:
    """Loads channel URLs from the channels file."""
    print(f"Loading channels: {channels_file_path}")
    if not os.path.exists(channels_file_path): log_error(f"FATAL: Channels file '{channels_file_path}' not found."); raise FileNotFoundError(f"{channels_file_path}")
    try:
        with open(channels_file_path, "r", encoding="utf-8") as file:
            channels = [line.strip() for line in file if line.strip() and not line.startswith('#')]
    except Exception as e: log_error(f"FATAL: Error reading channels file '{channels_file_path}': {e}"); raise
    if not channels: log_error("FATAL: Channels file empty."); raise ValueError("Channels file is empty.")
    print(f"Loaded {len(channels)} channels."); return channels


def load_cache(cache_file: str) -> dict:
    """Loads a JSON dictionary cache file, returning an empty dict on error or wrong type."""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f: content = f.read().strip()
            if not content: print(f"Cache file '{cache_file}' is empty."); return {}
            cache_data = json.loads(content)
            if isinstance(cache_data, dict): print(f"Loaded cache from '{cache_file}'."); return cache_data
            else: log_error(f"Warn: Cache '{cache_file}' invalid type {type(cache_data)}. Starting fresh."); return {}
        except json.JSONDecodeError as e: log_error(f"Warn: Error decoding cache '{cache_file}': {e}. Starting fresh."); return {}
        except Exception as e: log_error(f"Warn: Error reading cache '{cache_file}': {e}. Starting fresh."); return {}
    else: print(f"Cache file '{cache_file}' not found. Starting fresh."); return {}


def save_cache(cache: dict, cache_file: str):
    """Saves a dictionary to a JSON cache file."""
    try:
        if not isinstance(cache, dict): log_error(f"Save cache aborted: not dict '{cache_file}'."); return
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=4)
    except Exception as e:
        log_error(f"Error saving cache '{cache_file}': {e}")

def save_metadata_file(entry, video_index, seo_metadata, channel_url=None):
    """Saves the combined metadata to a JSON file, including channel URL as discovery_keyword."""
    original_title = entry.get("title", f"unk_{video_index}")
    uploader = entry.get("uploader", DEFAULT_UPLOADER_NAME)
    view_count = entry.get('view_count', 0);
    try:
        view_count = int(view_count) if view_count is not None else 0
    except: view_count = 0
    credit_uploader_name = uploader if uploader != DEFAULT_UPLOADER_NAME else "Original Uploader"
    optimized_description = seo_metadata.get("description", ""); credit_line = f"Credit: {credit_uploader_name}"
    if optimized_description and credit_line not in optimized_description: optimized_description += f"\n\n{credit_line}"
    elif not optimized_description: optimized_description = f"Default description.\n\n{credit_line}"
    metadata = {
        "video_index": str(video_index),
        "id": entry.get("id"),
        "original_title": original_title,
        "uploader": uploader,
        "view_count": view_count,
        "download_timestamp": datetime.now().isoformat(), # Use ISO format
        "optimized_title": seo_metadata.get("title", f"{original_title[:80]} #Shorts"),
        "optimized_description": optimized_description,
        "optimized_tags": seo_metadata.get("tags", []),
        "discovery_keyword": channel_url, # Store channel URL as discovery_keyword for correlation cache
        "metadata_strategy": "B: Channel-Based" # Strategy marker to differentiate from keyword-based downloads
    }
    metadata_file_path = os.path.join(metadata_folder, f"video{video_index}.json")
    try:
        with open(metadata_file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        return metadata
    except Exception as e:
        log_error(f"Error saving metadata {metadata_file_path}: {e}")
        return metadata # Return potentially incomplete data


# --- Main Execution Logic ---
def main():
    wb = None; downloaded_sheet = None
    downloaded_video_data = []
    previously_downloaded_videos = set()
    playlist_cache = {} # Processed video ID cache {channel_url: [ids]}
    channel_listing_cache = {} # Channel entry list cache {channel_url: [entries]}

    try:
        print("--- Starting Downloader Script ---")
        create_folders()
        wb, downloaded_sheet, _, previously_downloaded_videos = load_or_create_excel()
        channels = load_channels()
        playlist_cache = load_cache(channel_processed_ids_cache_file)
        channel_listing_cache = load_cache(channel_listing_cache_file) # Load permanent channel list cache

        video_counter = get_last_video_index(downloaded_sheet)

        # Calculate quotas
        num_channels = len(channels); channel_quotas = {}
        if num_channels > 0:
            base_quota = max(0, max_downloads // num_channels); remainder = max(0, max_downloads % num_channels)
            channel_quotas = {c: base_quota for c in channels}; channels_list = list(channels)
            for i in range(remainder): channel_quotas[channels_list[i % num_channels]] += 1
        else: print("Warning: No channels loaded.")
        print(f"Channel download quotas: {channel_quotas}")

        total_downloaded_this_run = 0
        channel_download_counts = {channel: 0 for channel in channels}

        if not os.path.exists(ffmpeg_path): print(f"Warning: ffmpeg not found: {ffmpeg_path}")

        # --- Channel Loop ---
        for channel_url in channels:
            if total_downloaded_this_run >= max_downloads: print("\nReached total download limit."); break
            channel_quota = channel_quotas.get(channel_url, 0)
            if channel_quota <= 0 or channel_download_counts[channel_url] >= channel_quota: continue

            # Ensure playlist cache list exists for the channel
            if channel_url not in playlist_cache: playlist_cache[channel_url] = []

            print(f"\nProcessing Channel: {channel_url} (Quota Left: {channel_quota - channel_download_counts[channel_url]})")

            # --- Channel Listing Cache Logic (Permanent) ---
            fetched_entries = []
            use_cache = False
            # Check if channel data exists in the permanent listing cache
            if channel_url in channel_listing_cache and isinstance(channel_listing_cache.get(channel_url), list):
                fetched_entries = channel_listing_cache[channel_url]
                if fetched_entries: # Ensure cached list is not empty
                    use_cache = True
                    print(f"  Using permanently cached video list ({len(fetched_entries)} entries).")
                else:
                    # Cached list is empty, treat as uncached
                    print(f"  Cached list for {channel_url} is empty. Will refetch.")
                    # Optionally remove empty entry: del channel_listing_cache[channel_url]
            # --- End Cache Check ---

            # --- Fetch list ONLY if not found in cache or cache was empty ---
            if not use_cache:
                playlist_limit = YT_PLAYLIST_FETCH_LIMIT
                print(f"Fetching video list (up to {playlist_limit}, this may take time)...")
                # Ensure shorts_url is defined before use
                shorts_url = f"{channel_url}/shorts"
                ydl_opts_fetch = { 'extract_flat': 'discard_in_playlist', 'playlistend': playlist_limit, 'quiet': True, 'no_warnings': True, 'ignoreerrors': True, 'skip_download': True, 'forcejson': True, 'socket_timeout': 60, }
                try:
                    with yt_dlp.YoutubeDL(ydl_opts_fetch) as ydl:
                        result = ydl.extract_info(shorts_url, download=False) # Use shorts_url here

                    if result and 'entries' in result and isinstance(result['entries'], list):
                        fetched_entries = [e for e in result['entries'] if e and isinstance(e, dict)]
                        print(f"  Finished fetching list. Found {len(fetched_entries)} entries.")
                        if fetched_entries: # Save ONLY if entries were found
                            channel_listing_cache[channel_url] = fetched_entries
                            save_cache(channel_listing_cache, channel_listing_cache_file)
                            print(f"  Saved fetched list to permanent cache for {channel_url}.")
                        else: log_error(f"Fetched 0 valid entries for {channel_url}.")
                    else:
                        print(f"  No entries found/extracted for {channel_url}.")
                        log_error(f"No entries/bad format: {channel_url}.")
                        continue
                except Exception as e:
                    print(f"  Error fetching list: {e}")
                    log_error(f"Error fetching list {channel_url}: {e}")
                    continue
            # --- End Fetch list ---

            if not fetched_entries: continue # Skip if still no entries

            # Sort and process entries
            def get_view_count(entry):
                try: return int(entry.get('view_count')) if entry.get('view_count') is not None else 0;
                except: return 0
            sorted_entries = sorted(fetched_entries, key=get_view_count, reverse=True)

            # --- Video Loop ---
            for entry in sorted_entries:
                if total_downloaded_this_run >= max_downloads: break
                if channel_download_counts[channel_url] >= channel_quota: break

                video_id = entry.get("id"); original_title = entry.get('title', '').strip(); uploader = entry.get('uploader', DEFAULT_UPLOADER_NAME).strip()
                if not video_id or not original_title: continue

                if not isinstance(playlist_cache.get(channel_url), list): playlist_cache[channel_url] = [] # Sanity check
                if str(video_id) in playlist_cache[channel_url]: continue # Check Processed ID cache
                if (original_title, uploader) in previously_downloaded_videos: # Check Title/Uploader cache
                    if str(video_id) not in playlist_cache[channel_url]: playlist_cache[channel_url].append(str(video_id))
                    continue

                video_url = entry.get('url')
                if not video_url: continue

                # --- Prepare filenames & Check existence ---
                video_file_name = f"video{video_counter}.mp4"; video_file_path = os.path.join(download_folder, video_file_name)
                metadata_file_name = f"video{video_counter}.json"; metadata_file_path = os.path.join(metadata_folder, metadata_file_name)
                video_exists = os.path.exists(video_file_path); metadata_exists = os.path.exists(metadata_file_path)

                if video_exists and metadata_exists: video_counter += 1; continue # Skip if both exist
                elif video_exists and not metadata_exists: # Regenerate metadata if needed
                    print(f"  Video {video_file_name} exists, metadata missing. Regenerating...")
                    seo_metadata = generate_metadata_with_timeout(original_title, seo_channel_name, seo_channel_topic, seo_example_tags, seo_example_hashtags, uploader)
                    generated_metadata = save_metadata_file(entry, video_counter, seo_metadata, channel_url)
                    if generated_metadata:
                        ts = generated_metadata.get("download_timestamp", datetime.now().isoformat()); views = generated_metadata.get('view_count', 0)
                        downloaded_video_data.append((f"video{video_counter}", generated_metadata.get("optimized_title"), ts, views, generated_metadata.get("uploader"), generated_metadata.get("original_title")))
                        playlist_cache[channel_url].append(str(video_id)); previously_downloaded_videos.add((original_title, uploader))
                        total_downloaded_this_run += 1; channel_download_counts[channel_url] += 1; video_counter += 1
                    else: log_error(f"Failed regenerating metadata for {video_file_name}."); video_counter += 1
                    continue

                # --- Download ---
                print(f"  Attempting download: {video_file_name}...")
                # Format string updated slightly for clarity/preference, functionality same
                ydl_opts_download = {
                    'format': 'bestvideo[height>=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio/bestvideo[height>=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio/best',
                    'outtmpl': video_file_path, 'quiet': True, 'no_warnings': True,
                    'ignoreerrors': False, 'ffmpeg_location': ffmpeg_path,
                    'merge_output_format': 'mp4', 'retries': 2,
                 }
                download_success = False
                try:
                    with yt_dlp.YoutubeDL(ydl_opts_download) as ydl_download: ydl_download.download([video_url])
                    if os.path.exists(video_file_path) and os.path.getsize(video_file_path) > 1024: download_success = True
                except Exception as e:
                    log_error(f"Download error {video_id} ({original_title}): {e}")
                if download_success:
                    # --- Post-Download ---
                    print(f"  Download ok. Generating metadata...")
                    seo_metadata = generate_metadata_with_timeout(original_title, seo_channel_name, seo_channel_topic, seo_example_tags, seo_example_hashtags, uploader)
                    generated_metadata = save_metadata_file(entry, video_counter, seo_metadata, channel_url)
                    if generated_metadata:
                        ts = generated_metadata.get("download_timestamp", datetime.now().isoformat()); views = generated_metadata.get('view_count', 0)
                        downloaded_video_data.append((f"video{video_counter}", generated_metadata.get("optimized_title"), ts, views, generated_metadata.get("uploader"), generated_metadata.get("original_title")))
                        playlist_cache[channel_url].append(str(video_id)); previously_downloaded_videos.add((original_title, uploader))
                        video_counter += 1; total_downloaded_this_run += 1; channel_download_counts[channel_url] += 1
                        print(f"  Processed video {video_counter-1} successfully.") # Confirmation log
                    else: # Metadata failed, delete video
                        log_error(f"Metadata failed {video_id}. Deleting video.");
                        if os.path.exists(video_file_path):
                            try: os.remove(video_file_path); print("  Deleted orphaned video.")
                            except OSError as e: log_error(f"Could not delete orphaned video: {e}")
                elif os.path.exists(video_file_path): # Cleanup partial download
                        try:
                            os.remove(video_file_path)
                        except OSError:
                            pass # Or log error
            # --- End Video Loop ---

            print(f"  Finished channel {channel_url}. Saving intermediate Processed ID cache.")
            save_cache(playlist_cache, channel_processed_ids_cache_file) # Save only processed IDs cache here

        # --- End Channel Loop ---
        print("\n--- Finished processing channels or reached download limit. ---")

    except KeyboardInterrupt: print("\n--- Interrupted by user (Ctrl+C). ---"); log_error("Interrupted by user.")
    except Exception as e: error_message = f"FATAL error in main loop: {e}"; print(error_message); log_error(error_message); print("\n--- Traceback ---"); traceback.print_exc(); print("-----------------\n"); log_error(f"Traceback:\n{traceback.format_exc()}")
    finally:
        # --- Final Save Operations ---
        print("\n--- Entering final cleanup and save phase. ---")
        # Save Excel Data
        if wb and downloaded_sheet and downloaded_video_data:
            print(f"Attempting final Excel update ({len(downloaded_video_data)} new)...")
            try:
                 def get_sort_key(item):
                     try: return int(item[3]) if len(item)>3 and item[3] is not None else 0;
                     except: return 0
                 print("  Sorting data..."); downloaded_video_data.sort(key=get_sort_key, reverse=True);
                 print("  Appending rows...");
                 for row_data in downloaded_video_data:
                      if len(row_data) == len(EXPECTED_DOWNLOADED_HEADERS): downloaded_sheet.append(row_data)
                      else: log_error(f"Skipping Excel row, wrong count: {row_data}")
                 print("  Saving workbook..."); wb.save(excel_file); print("Excel saved.")
            except Exception as e:
                 error_message = f"CRITICAL: Error saving Excel: {e}"; print(error_message); log_error(error_message); traceback.print_exc(); log_error(f"Excel save Traceback:\n{traceback.format_exc()}")
                 backup_file = os.path.join(script_directory, f"excel_backup_data_{datetime.now():%Y%m%d_%H%M%S}.json")
                 print(f"Attempting backup to {backup_file}...");
                 try:
                     with open(backup_file, "w", encoding='utf-8') as bf: json.dump(downloaded_video_data, bf, indent=4); log_error(f"Saved backup {backup_file}."); print("Backup saved.")
                 except Exception as be:
                     log_error(f"CRITICAL: Failed backup save: {be}")
                     print(f"CRITICAL: Failed backup save: {be}")

        elif not downloaded_video_data: print("\nNo new videos processed. No Excel data to save.")

        # Save Caches
        print("\nSaving final caches...")
        if isinstance(playlist_cache, dict): save_cache(playlist_cache, channel_processed_ids_cache_file); print("Channel Processed IDs cache saved.")
        else: log_error("Playlist cache invalid type. Skipping save.")
        # Save the channel listing cache one last time
        if isinstance(channel_listing_cache, dict): save_cache(channel_listing_cache, channel_listing_cache_file); print("Channel listing cache saved.")
        else: log_error("Channel listing cache invalid type. Skipping save.")

        print("\n--- Downloader script execution finished. ---")

# --- Script Entry Point ---
if __name__ == "__main__":
    main()
