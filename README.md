# YiffScraper V3.0

Welcome to YiffScraper, an asynchronous, multi-threaded image scraper dedicated to retrieving images from e621. This tool is currently in **public beta** and under active development. Feedback, suggestions, and contributions are welcome!

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contribution](#contribution)

## Overview

YiffScraper allows users to fetch and download images from e621 using specified tags, with additional capabilities like multi-threaded downloading and zipping the downloaded files for user convenience.

## Features

- **Multi-Threaded Download**: Download multiple images concurrently.
- **Tag Builder**: Helps users to build tag queries through a guided Q&A session.
- **Tag Loader**: Ability to load tags from a file.
- **Tag Saver**: Save built tags for future use.
- **Zip Downloaded Files**: Option to zip all downloaded files into a single archive.
- **Debug Mode**: Get insights into what the scraper is doing in the backend.
- **GUI for File Operations**: GUI window to choose files for tag loading and saving.
  
## Installation

Navigate to releases and download the latest EXE file to run, or to run from source:

1. **Clone the Repository**
   ```shell
   git clone https://github.com/LiterallyAxo/YiffScraper.git
   ```
   
2. **Install Dependencies**
   Navigate to the cloned repository and install the necessary Python packages:
   ```shell
   pip install aiohttp aiofiles asyncio Pillow colorama pystyle
   ```
   
3. **Run the Script**
   Launch the scraper using Python:
   ```shell
   python main.py
   ```
   
## Usage

Upon running the script, you will be greeted by the main menu:

1. **Start**: Begins the scraping process.
2. **Exit**: Closes the application.

During the scraping setup, you'll go through several prompts:

- **Debug Mode**: Optional insight into the backend processes.
- **Tag Selection**: Choose to enter tags manually, build them using a guided process, or load them from a file.
- **Download Folder**: Specify the name of the folder where the images will be saved.
- **Image & Thread Quantity**: Determine the number of images to download and the number of threads for downloading.

The tag builder assists in constructing a tag string based on your preferences, such as gender, score, rating, and any additional kinks or fetishes.

## Contribution

Contributions are welcomed! Feel free to fork the repository and submit your pull requests. For major changes, kindly open an issue first to discuss what you'd like to modify.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
