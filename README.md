Nubaish Downloader

A lightweight, animated YouTube video and audio downloader CLI written in Python.

Nubaish Downloader is a terminal-based downloader featuring an interactive interface, video quality selection, MP3 audio extraction, playlist support and download history.

Features

- 🎬 Download videos with selectable quality.
- 🎵 Extract audio in MP3 format.
- ⚡ Download videos in the best available quality.
- 📋 Support for YouTube playlists.
- 📊 Animated download progress indicator.
- 📁 Custom download directory.
- 📜 Download history.
- 🎨 Colourful animated terminal interface.
- 💻 Cross-platform design.

Supported Platforms

- Android (Termux)
- Windows
- Linux
- macOS

Requirements

- Python 3.8 or newer.
- FFmpeg (required for audio conversion and certain format-merging operations).
- Internet connection.

Installation

1. Clone the repository

git clone https://github.com/YOUR_USERNAME/nubaish-downloader.git

2. Enter the project directory

cd nubaish-downloader

3. Install dependencies

pip install -r requirements.txt

4. Run the application

python nubaish_downloader.py

Android (Termux) Installation

Install Termux and execute:

pkg update && pkg upgrade
pkg install python git ffmpeg

Clone the repository:

git clone https://github.com/YOUR_USERNAME/nubaish-downloader.git
cd nubaish-downloader

Install dependencies:

pip install -r requirements.txt

Grant storage access:

termux-setup-storage

Run:

python nubaish_downloader.py

Usage

Interactive Mode

python nubaish_downloader.py

Download a video

python nubaish_downloader.py -u "VIDEO_URL" -b

Download audio (MP3)

python nubaish_downloader.py -u "VIDEO_URL" -a

Show video information

python nubaish_downloader.py -u "VIDEO_URL" -i

Download a specific format

python nubaish_downloader.py -u "VIDEO_URL" -q FORMAT_ID

Limit playlist downloads

python nubaish_downloader.py -u "PLAYLIST_URL" -b --playlist-limit 5

Custom download directory

python nubaish_downloader.py -u "VIDEO_URL" -b -o "./downloads"

Show download history

python nubaish_downloader.py --history

Display version

python nubaish_downloader.py --version

Display available commands

python nubaish_downloader.py --help

Dependencies

- "yt-dlp" (https://github.com/yt-dlp/yt-dlp) — Video and audio extraction.
- FFmpeg — Audio conversion and media merging.

Disclaimer

Nubaish Downloader is an independent open-source project and is not affiliated with, endorsed by, or sponsored by YouTube.

Users are responsible for ensuring that their downloads comply with applicable copyright laws, content owners' permissions and the terms of the platforms they use.

Do not use this software to infringe copyright or violate applicable laws.

License

This project is licensed under the MIT License. See the "LICENSE" (LICENSE) file for details.

Author

Nubaish

GitHub: https://github.com/YOUR_USERNAME

---

If you find this project useful, consider giving it a ⭐ on GitHub!
