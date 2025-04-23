from setuptools import setup, find_packages

setup(
    name="youtube-shorts-automation",
    version="1.0.0",
    description="A suite of tools for automating YouTube Shorts creation and management",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.3.0",
        "yt-dlp>=2023.3.4",
        "openpyxl>=3.1.0",
        "colorama>=0.4.6",
        "selenium>=4.10.0",
        "webdriver-manager>=3.8.6",
    ],
    entry_points={
        "console_scripts": [
            "yt-track=youtube_shorts.performance_tracker:main",
            "yt-download=youtube_shorts.downloader:main",
            "yt-upload=youtube_shorts.uploader:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Multimedia :: Video",
        "Topic :: Internet",
    ],
)
