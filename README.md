# YouTube Shorts Automation Suite with Self-Improvement

This suite of scripts automates the entire YouTube Shorts workflow - from finding videos to tracking performance. It includes advanced self-improvement features that use AI to analyze performance, optimize metadata, and suggest improvements.

## Components

The suite consists of three main scripts:

1. **Performance Tracker** (`performance_tracker.py`): Collects performance metrics from uploaded videos
2. **Downloader** (`downloader.py`): Finds and downloads new videos with SEO optimization and self-improvement
3. **Uploader** (`uploader.py`): Uploads the videos to YouTube with optimized metadata

These components work together to create a complete automation pipeline for YouTube Shorts.

## Features

### Downloader Features
- **SEO-Focused Metadata Generation**: Creates highly optimized titles, descriptions, and tags
- **Performance-Based Keyword Selection**: Learns which keywords lead to better-performing videos
- **Dynamic Keyword Management**: Adds new keywords and removes underperforming ones
- **Metadata Prompt Refinement**: Automatically improves the prompt used for metadata generation
- **Parameter Tuning Suggestions**: Analyzes performance metrics to suggest configuration changes

### Uploader Features
- **Automated Uploads**: Batch upload videos to YouTube as Shorts
- **Metadata Management**: Apply optimized titles, descriptions, and tags
- **Scheduling**: Schedule videos for future publication
- **Error Handling**: Robust error detection and recovery
- **Performance Tracking**: Track upload success rates and error patterns
- **AI-Assisted Analysis**: Use Google's Gemini AI to analyze errors and suggest improvements
- **Debug Recording**: Optional screen recording during uploads for troubleshooting

## Self-Improvement Features

The suite includes AI-powered self-improvement capabilities in both the downloader and uploader:

### Downloader Self-Improvement

- **Performance Feedback Loop**: Tracks how videos perform and adjusts keyword scores
- **Metadata Quality Analysis**: Monitors metadata generation success rates and improves the prompt
- **Parameter Tuning**: Analyzes overall performance and suggests configuration changes
- **Keyword Pool Management**: Dynamically adds new keywords and removes underperforming ones

### Uploader Self-Improvement

- **Performance Metrics Tracking**: Tracks upload attempts and successes
- **Error Categorization**: Categorizes and counts different types of errors
- **Error Sample Analysis**: Stores detailed error samples for analysis
- **AI-Assisted Error Analysis**: Uses Google's Gemini AI to analyze error patterns
- **Selector Optimization**: Recommends XPath selector updates, timeout adjustments, and other optimizations

### How to Use Self-Improvement Features

1. Add your Gemini API key to the `config.txt` file:
   ```
   API_KEY=your_gemini_api_key_here
   ```
   Get your API key from: https://aistudio.google.com/app/apikey

2. For uploader analysis, run with the `--analyze` or `-a` flag:
   ```
   python uploader_editing.py --analyze
   ```

3. For downloader, the self-improvement happens automatically during normal operation

4. Review the analysis in the console output and in the log files

5. Apply any suggested improvements to the configuration

## Configuration

Edit the `config.txt` file to customize the suite's behavior. Here's a detailed explanation of all available options:

```
# API Keys (Required for both downloader and uploader)
API_KEY=your_gemini_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here  # Same as API_KEY, used for AI features

# Download and Upload Limits
MAX_DOWNLOADS=6        # Maximum number of videos to download per run
MAX_UPLOADS=12         # Maximum number of videos to upload per run
MAX_KEYWORDS=200       # Maximum number of keywords to store

# Upload Settings
UPLOAD_CATEGORY=Gaming  # YouTube category for uploads

# --- Scheduling Settings ---

# Mode for scheduling uploads. Options:
#   default_interval = Publish first video now, schedule subsequent videos at fixed interval.
#   custom_tomorrow  = Try custom schedule times from config (for tomorrow onwards), then use fixed interval fallback. NO immediate publish.
SCHEDULING_MODE=custom_tomorrow

# Fixed interval (in minutes) used for scheduling in 'default_interval' mode
# AND as the fallback interval in 'custom_tomorrow' mode when custom slots are exhausted/invalid.
SCHEDULE_INTERVAL_MINUTES=240

# List of preferred schedule times (HH:MM AM/PM format, comma-separated) for 'custom_tomorrow' mode.
# The script will try to use these times sequentially for videos in a run, always targeting TOMORROW's date or later.
CUSTOM_SCHEDULE_TIMES=6:00 AM, 9:00 AM, 11:30 AM, 3:00 PM, 6:00 PM, 10:00 PM

# Minimum number of minutes ahead of the current time a video can be scheduled.
# Prevents scheduling too close to the current time, which YouTube might reject.
MIN_SCHEDULE_AHEAD_MINUTES=20

# Browser Profile
PROFILE_PATH=C:\Users\YourUsername\AppData\Roaming\Mozilla\Firefox\Profiles\yourprofile.default

# YouTube Limits (Character/Count Limits for Uploads)
YOUTUBE_DESCRIPTION_LIMIT=4950
YOUTUBE_TAG_LIMIT=100
YOUTUBE_TOTAL_TAGS_LIMIT=450
YOUTUBE_MAX_TAGS_COUNT=40

# Debug Recording Settings
# Enable screen recording for debugging (True/False). Requires FFmpeg installed.
ENABLE_DEBUG_RECORDING=False
# Optional: Specify full path to ffmpeg executable if not found automatically in system PATH
FFMPEG_PATH=C:\path\to\ffmpeg.exe
```

### Important Configuration Options

#### Scheduling Modes

- **default_interval**: Publishes the first video immediately and schedules subsequent videos at fixed intervals defined by `SCHEDULE_INTERVAL_MINUTES`.
- **custom_tomorrow**: Uses the times specified in `CUSTOM_SCHEDULE_TIMES` starting from tomorrow, then falls back to fixed intervals if needed. No videos are published immediately.

#### Firefox Profile

Using a dedicated Firefox profile is recommended for the uploader. This allows you to:
- Stay logged into YouTube
- Avoid login captchas
- Maintain session cookies

To create a new Firefox profile:
1. Open Firefox and type `about:profiles` in the address bar
2. Click "Create a New Profile" and follow the instructions
3. Copy the profile path from the "Root Directory" field
4. Paste it into the `PROFILE_PATH` setting in `config.txt`

## Excel File Structure

The system uses an Excel file (`shorts_data.xlsx`) with two sheets:

### Downloaded Sheet
- Video Index
- Optimized Title
- Downloaded Date
- Views
- Uploader
- Original Title

### Uploaded Sheet
- Video Index
- Optimized Title
- YouTube Video ID
- Upload Timestamp
- Scheduled Time
- Publish Status
- Views (YT)
- Likes (YT)
- Comments (YT)
- Last Updated

## Requirements

- Python 3.8+
- Required packages: `yt_dlp`, `google-generativeai`, `openpyxl`, `colorama`, `selenium`
- Firefox browser (for uploader)
- Google Gemini API key (for all AI features)
- FFmpeg (for video processing and optional debug recording)

## Installation

### Option 1: Standard Installation

1. Clone this repository
2. Install required packages: `pip install -r requirements.txt`
3. Configure `config.txt` with your settings
4. Create a `niche.txt` file with your target niche (e.g., "GTA 6")
5. Run each component as needed (see 'Running Individual Components' section below)

### Option 2: Package Installation

1. Clone this repository
2. Install the package in development mode: `pip install -e .`
3. Set up your workspace: `yt-setup` or `python -m youtube_shorts.setup_workspace`
4. Configure `config.txt` with your settings
5. Edit `niche.txt` with your target niche (e.g., "GTA 6")
6. Use the command-line tools:
   ```
   yt-track    # Run performance tracker
   yt-download # Run downloader
   yt-upload   # Run uploader
   ```

## Running Individual Components

### Using Python Directly

```
python performance_tracker.py
python downloader.py
python uploader.py
```

### Using Package Commands (if installed as a package)

```
yt-track   # Run performance tracker
yt-download # Run downloader
yt-upload   # Run uploader
```

## Error Types Tracked

### Uploader Error Types
- XPath Selector Errors
- Timeout Errors
- Network Errors
- WebDriver Errors
- Session Errors
- YouTube UI Change Errors
- Input Field Errors
- Click Interaction Errors
- Validation Errors
- File Operation Errors

### Downloader Error Types
- Metadata Generation Errors
- API Timeout Errors
- Download Failures
- Parsing Errors
- File Operation Errors

## Files

### Main Scripts
- `performance_tracker.py`: Tracks video performance metrics
- `downloader.py`: Downloads videos with SEO optimization and self-improvement
- `uploader.py`: Uploads videos to YouTube

### Package Structure
- `youtube_shorts/`: Package directory
  - `__init__.py`: Package initialization
  - `performance_tracker.py`: Performance tracking module
  - `downloader.py`: Video downloading module
  - `uploader.py`: Video uploading module

### Configuration and Data Files
- `setup.py`: Package setup script
- `requirements.txt`: Required dependencies
- `config.txt`: Configuration settings (created by setup script)
- `niche.txt`: Target niche for content (created by setup script)
- `shorts_data.xlsx`: Excel file tracking downloaded and uploaded videos (created by setup script)
- `seo_metadata_prompt.txt`: Cache for the potentially improved SEO prompt (created during runtime)
- `metadata_metrics.json`: Tracks metadata generation metrics (created by setup script)
- `performance_metrics.json`: Tracks overall performance metrics (created by setup script)

### Directories
- `shorts_downloads/`: Where downloaded videos are stored (created by setup script)
- `shorts_metadata/`: Where metadata files are stored (created by setup script)
- `youtube_shorts/data/`: Contains template files for configuration

## License

This project is licensed under the MIT License - see the LICENSE file for details.
