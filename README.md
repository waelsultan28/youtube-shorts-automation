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

Edit the `config.txt` file to customize the suite's behavior:

```
# API Key (Required for both downloader and uploader)
API_KEY=your_gemini_api_key_here

# Downloader Settings
MAX_DOWNLOADS=10
MAX_KEYWORDS=200

# Uploader Settings
MAX_UPLOADS=12
UPLOAD_CATEGORY=Gaming

# Scheduling Settings
SCHEDULING_MODE=custom_tomorrow
SCHEDULE_INTERVAL_MINUTES=240
CUSTOM_SCHEDULE_TIMES=6:00 AM, 9:00 AM, 11:30 AM, 3:00 PM, 6:00 PM, 10:00 PM

# Browser Profile
PROFILE_PATH=path/to/firefox/profile

# YouTube Limits
YOUTUBE_DESCRIPTION_LIMIT=4950
YOUTUBE_TAG_LIMIT=100
YOUTUBE_TOTAL_TAGS_LIMIT=450
YOUTUBE_MAX_TAGS_COUNT=40

# Debug Recording Settings
ENABLE_DEBUG_RECORDING=False
FFMPEG_PATH=path/to/ffmpeg.exe
```

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
3. Configure `config.txt` with your settings
4. Create a `niche.txt` file with your target niche (e.g., "GTA 6")
5. Use the command-line tools:
   ```
   yt-track   # Run performance tracker
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

### Configuration
- `setup.py`: Package setup script
- `requirements.txt`: Required dependencies
- `config.txt`: Configuration settings
- `niche.txt`: Target niche for content
- `shorts_data.xlsx`: Excel file tracking downloaded and uploaded videos
- `seo_metadata_prompt.txt`: Cache for the potentially improved SEO prompt
- `metadata_metrics.json`: Tracks metadata generation metrics
- `performance_metrics.json`: Tracks overall performance metrics
- `tuning_suggestions.log`: Stores parameter tuning suggestions

## Folders

- `shorts_downloads`: Downloaded video files
- `shorts_metadata`: Metadata JSON files for each video

## License

This project is licensed under the MIT License - see the LICENSE file for details.
