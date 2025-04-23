"""
YouTube Shorts Automation Suite

A collection of tools for automating the creation, optimization, and management of YouTube Shorts.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

# Import setup function for easy access
from .setup_workspace import setup_workspace

# Import main modules
from . import performance_tracker
from . import downloader
from . import uploader
from . import youtube_limits
