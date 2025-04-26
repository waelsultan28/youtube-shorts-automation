# Changelog

All notable changes to the YouTube Shorts Automation Suite will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2023-07-15

### Added
- Excel auto-closing functionality to prevent permission errors when saving Excel files
- New `excel_utils.py` module with robust Excel handling functions
- Process management for Excel using psutil library
- Automatic backup creation before saving Excel files
- Retry mechanics for Excel operations with exponential backoff
- Multiple fallback save methods for Excel data
- JSON data backup when Excel saves fail completely

### Changed
- Updated all scripts to use the new Excel utilities
- Enhanced error handling for Excel operations
- Improved logging for Excel-related operations
- Added graceful degradation when Excel utilities are not available
- Updated requirements.txt to include psutil library

### Fixed
- Permission errors when saving Excel files while they are open in Excel
- Data loss issues when Excel saves fail

## [1.1.0] - 2023-06-20

### Added
- Dynamic Category Suggestion using Gemini AI
- Smart Category Selection in uploader with fallback to default configuration
- Channel-Based Downloader for downloading videos from specific YouTube channels
- Integration between keyword-based and channel-based downloaders

### Fixed
- Issue where info.json file was deleted before tag extraction
- Various code improvements and optimizations

## [1.0.0] - 2023-05-15

### Added
- Initial release of YouTube Shorts Automation Suite
- Keyword-based downloader with SEO optimization
- Uploader with scheduling capabilities
- Performance tracker for YouTube metrics
- Self-improvement features using Gemini AI
