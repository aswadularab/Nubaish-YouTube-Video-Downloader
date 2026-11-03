#!/usr/bin/env python3
"""
Nubaish Downloader - Multi-Website Media Downloader
Version: 1.1.0
Author: Nubaish
"""

import os
import sys
import time
import shutil
import subprocess
import threading
import itertools
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("[!] yt-dlp is not installed.")
    print("    Install it using: pip install -U yt-dlp")
    sys.exit(1)


__version__ = "1.1.0"
APP_NAME = "Nubaish Downloader"

# Enable ANSI colors on Windows
if os.name == "nt":
    os.system("")


# ───────────────────────── colors ─────────────────────────

class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"


# ───────────────────────── config ─────────────────────────

FOLDER_NAME = "nubaish Downloader"


def get_download_dir():
    """Choose a suitable download directory for each platform."""

    custom_path = os.environ.get("NUBAISH_DOWNLOAD_DIR")

    if custom_path:
        return Path(custom_path).expanduser()

    android_storage = Path("/storage/emulated/0")

    if android_storage.exists():
        base_path = android_storage
    else:
        base_path = Path.home() / "Downloads"

    return base_path / FOLDER_NAME


DOWNLOAD_DIR = get_download_dir()


# ─────────────────────── UI helpers ───────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def reveal(text, color=C.CYAN, delay=0.02, bold=True, newline=True):
    """Slow character-by-character reveal."""

    sys.stdout.write(color + (C.BOLD if bold else ""))

    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)

    sys.stdout.write(C.RESET)

    if newline:
        sys.stdout.write("\n")

    sys.stdout.flush()


def spinner(message, stop_event, delay=0.15):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼",
              "⠴", "⠦", "⠧", "⠇", "⠏"]

    for frame in itertools.cycle(frames):
        if stop_event.is_set():
            break

        sys.stdout.write(
            f"\r{C.CYAN}{C.BOLD}{frame} {message}{C.RESET}"
        )
        sys.stdout.flush()
        time.sleep(delay)

    sys.stdout.write("\r" + " " * (len(message) + 4) + "\r")
    sys.stdout.flush()


def section(title):
    bar = f"{C.MAGENTA}{C.BOLD}{'─' * 42}{C.RESET}"

    print(bar)
    reveal(f"  {title}", color=C.WHITE, delay=0.02)
    print(bar)


def human_size(num):
    if num is None:
        return "?"

    for unit in ["B", "KB", "MB", "GB"]:
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024

    return f"{num:.1f} TB"


def human_duration(sec):
    if sec is None:
        return "?"

    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)

    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"


# ───────────────────────── banner ─────────────────────────

BANNER_ART = [
    r"   _   _ _   _ ____    _    ___ ____  _   _ ",
    r"  | \ | | | | | __ )  / \  |_ _/ ___|| | | |",
    r"  |  \| | | | |  _ \ / _ \  | |\___ \| |_| |",
    r"  | |\  | |_| | |_) / ___ \ | | ___) |  _  |",
    r"  |_| \_|\___/|____/_/   \_\___|____/|_| |_|",
]


def show_banner():

    for line in BANNER_ART:
        reveal(line, color=C.CYAN, delay=0.004)
        time.sleep(0.06)

    time.sleep(0.15)

    reveal("  ──────────────────────────────────────────",
           color=C.MAGENTA, delay=0.006)

    reveal("       M U L T I - W E B S I T E",
           color=C.YELLOW, delay=0.025)

    reveal("          M E D I A   D O W N L O A D E R",
           color=C.YELLOW, delay=0.025)

    reveal(f"            v{__version__}  ·  by Nubaish",
           color=C.GREEN, delay=0.025)

    reveal("  ──────────────────────────────────────────",
           color=C.MAGENTA, delay=0.006)

    time.sleep(0.2)


# ─────────────────────── folder setup ─────────────────────

def ensure_folder():

    try:
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

        reveal(
            f"✔ Folder ready: {DOWNLOAD_DIR}",
            color=C.GREEN,
            delay=0.008
        )

    except OSError as e:
        reveal(
            f"✘ Cannot create folder: {e}",
            color=C.RED,
            delay=0.008
        )
        sys.exit(1)


# ────────────────────── yt-dlp helpers ────────────────────

def fetch_info(url):

    stop = threading.Event()

    t = threading.Thread(
        target=spinner,
        args=("Fetching media information...", stop, 0.15)
    )

    t.start()

    try:
        options = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": False,
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)

        return info

    finally:
        stop.set()
        t.join()


def get_format_info(info):
    """
    Get format information.
    For playlists, use the first available entry containing formats.
    """

    if info.get("formats"):
        return info

    entries = info.get("entries") or []

    for entry in entries:
        if entry and entry.get("formats"):
            return entry

    return info


def list_video_formats(info):

    fmts = [
        f for f in info.get("formats", [])
        if f.get("vcodec") not in (None, "none")
        and f.get("ext") != "mhtml"
    ]

    fmts.sort(
        key=lambda f: (
            f.get("height") or 0,
            f.get("tbr") or 0
        ),
        reverse=True
    )

    return fmts


def check_ffmpeg():

    if shutil.which("ffmpeg"):
        return True

    reveal(
        "FFmpeg was not found. Some download operations require it.",
        color=C.YELLOW
    )

    return False


# ─────────────────────── progress hook ────────────────────

def make_progress_hook():

    width = 30

    def hook(d):

        if d["status"] == "downloading":

            total = (
                d.get("total_bytes")
                or d.get("total_bytes_estimate")
                or 0
            )

            done = d.get("downloaded_bytes", 0)

            if total <= 0:
                return

            pct = min(done / total, 1)
            filled = int(width * pct)

            bar = (
                "█" * filled
                + "░" * (width - filled)
            )

            speed = d.get("speed") or 0
            eta = d.get("eta") or 0

            sys.stdout.write(
                f"\r  {C.GREEN}{C.BOLD}[{bar}]{C.RESET} "
                f"{C.CYAN}{C.BOLD}{pct * 100:5.1f}%{C.RESET}  "
                f"{C.BOLD}{human_size(done)}/{human_size(total)}{C.RESET}  "
                f"{C.YELLOW}{C.BOLD}{human_size(speed)}/s{C.RESET}  "
                f"{C.DIM}ETA {human_duration(eta)}{C.RESET}"
            )

            sys.stdout.flush()

        elif d["status"] == "finished":

            print(
                f"\n  {C.GREEN}{C.BOLD}"
                "✔ Download finished, post-processing..."
                f"{C.RESET}"
            )

    return hook


# ──────────────────────── actions ─────────────────────────

def action_video(url):

    info = fetch_info(url)
    format_info = get_format_info(info)

    fmts = list_video_formats(format_info)

    if not fmts:
        reveal(
            "No video formats found.",
            color=C.RED
        )
        return

    section("AVAILABLE VIDEO FORMATS")

    for i, f in enumerate(fmts, 1):

        size = f.get("filesize") or f.get("filesize_approx")

        print(
            f"  {C.GREEN}{C.BOLD}[{i:>2}]{C.RESET} "
            f"{C.BOLD}id={C.CYAN}{f.get('format_id'):<10}{C.RESET} "
            f"{C.BOLD}ext={f.get('ext') or '?':<5} "
            f"res={C.YELLOW}{f.get('resolution') or '?':<12}{C.RESET} "
            f"{C.BOLD}fps={f.get('fps') or '?':<4} "
            f"size={human_size(size)}{C.RESET}"
        )

    try:

        n = int(input(
            f"\n{C.BOLD}Choose format # › {C.RESET}"
        ))

        if not 1 <= n <= len(fmts):
            raise ValueError

        chosen = fmts[n - 1]

    except (ValueError, IndexError):

        reveal(
            "Invalid choice.",
            color=C.RED
        )
        return

    fid = chosen["format_id"]

    if chosen.get("acodec") == "none":
        fmt = f"{fid}+bestaudio/best"
    else:
        fmt = fid

    run_download(url, fmt)


def action_audio(url):

    if not check_ffmpeg():
        reveal(
            "MP3 conversion cancelled. Install FFmpeg first.",
            color=C.RED
        )
        return

    run_download(
        url,
        "bestaudio/best",
        postprocess_mp3=True
    )


def action_best(url):

    if not check_ffmpeg():
        reveal(
            "Best-quality download may require FFmpeg for merging.",
            color=C.YELLOW
        )
        return

    run_download(
        url,
        "bestvideo+bestaudio/best"
    )


def action_show(url):

    info = fetch_info(url)

    section("MEDIA INFORMATION")

    print(
        f"  {C.BOLD}Title    :{C.RESET} "
        f"{C.YELLOW}{C.BOLD}{info.get('title') or '?'}{C.RESET}"
    )

    print(
        f"  {C.BOLD}Uploader :{C.RESET} "
        f"{info.get('uploader') or '?'}"
    )

    print(
        f"  {C.BOLD}Duration :{C.RESET} "
        f"{human_duration(info.get('duration'))}"
    )

    if info.get("view_count") is not None:
        print(
            f"  {C.BOLD}Views    :{C.RESET} "
            f"{info['view_count']:,}"
        )

    print(
        f"  {C.BOLD}Extractor:{C.RESET} "
        f"{info.get('extractor_key') or '?'}"
    )

    entries = info.get("entries")

    if entries:
        count = sum(1 for entry in entries if entry)
        print(
            f"  {C.BOLD}Playlist :{C.RESET} "
            f"{count} items"
        )

    print(
        f"  {C.BOLD}Formats  :{C.RESET} "
        f"{len(info.get('formats', []))}"
    )


# ─────────────────────── open folder ──────────────────────

def open_folder():

    try:

        if os.name == "nt":

            os.startfile(str(DOWNLOAD_DIR))

        elif sys.platform == "darwin":

            subprocess.Popen(["open", str(DOWNLOAD_DIR)])

        elif shutil.which("termux-open"):

            subprocess.Popen([
                "termux-open",
                str(DOWNLOAD_DIR)
            ])

        elif shutil.which("xdg-open"):

            subprocess.Popen([
                "xdg-open",
                str(DOWNLOAD_DIR)
            ])

        else:

            reveal(
                f"Folder location: {DOWNLOAD_DIR}",
                color=C.YELLOW
            )
            return

        reveal(
            f"Opened: {DOWNLOAD_DIR}",
            color=C.GREEN
        )

    except Exception as e:

        reveal(
            f"Could not open folder: {e}",
            color=C.RED
        )


# ─────────────────────── download engine ──────────────────

def run_download(url, format_selector, postprocess_mp3=False):

    outtmpl = str(
        DOWNLOAD_DIR / "%(title)s [%(id)s].%(ext)s"
    )

    opts = {
        "format": format_selector,
        "outtmpl": outtmpl,
        "progress_hooks": [make_progress_hook()],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": False,
        "ignoreerrors": False,
        "retries": 3,
        "fragment_retries": 3,
    }

    if postprocess_mp3:

        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    else:

        opts["merge_output_format"] = "mp4"

    section("DOWNLOADING")

    print(
        f"  {C.BOLD}URL    :{C.RESET} "
        f"{C.CYAN}{url}{C.RESET}"
    )

    print(
        f"  {C.BOLD}Format :{C.RESET} "
        f"{C.YELLOW}{format_selector}{C.RESET}"
    )

    print(
        f"  {C.BOLD}Save   :{C.RESET} "
        f"{C.CYAN}{DOWNLOAD_DIR}{C.RESET}\n"
    )

    try:

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        reveal(
            f"\n✔ Done! Saved to {DOWNLOAD_DIR}",
            color=C.GREEN,
            delay=0.015
        )

    except Exception as e:

        reveal(
            f"\n✘ Download failed: {e}",
            color=C.RED,
            delay=0.015
        )


# ───────────────────────── main menu ──────────────────────

def print_menu():

    section("MAIN MENU")

    items = [
        ("1", "Download Video (choose quality)", C.GREEN),
        ("2", "Download Audio only (MP3)", C.GREEN),
        ("3", "Best quality (auto)", C.GREEN),
        ("4", "Show info / formats only", C.GREEN),
        ("5", "Open download folder", C.GREEN),
        ("0", "Exit", C.RED),
    ]

    for key, label, color in items:

        reveal(
            f"  [{key}]  {label}",
            color=color,
            delay=0.012
        )

        time.sleep(0.03)

    print(
        f"{C.MAGENTA}{C.BOLD}{'─' * 42}{C.RESET}"
    )


# ───────────────────────── interactive mode ───────────────

def interactive_mode():

    while True:

        print()
        print_menu()

        choice = input(
            f"{C.BOLD}{C.WHITE}Select option › {C.RESET}"
        ).strip()

        if choice == "0":

            reveal(
                "\n  Thanks for using Nubaish Downloader. Bye! 👋",
                color=C.GREEN,
                delay=0.03
            )
            break

        if choice == "5":

            open_folder()

            input(
                f"\n{C.DIM}Press Enter to return...{C.RESET}"
            )
            continue

        if choice not in {"1", "2", "3", "4"}:

            reveal(
                "Unknown option.",
                color=C.RED
            )
            continue

        url = input(
            f"\n{C.BOLD}Media URL › {C.RESET}"
        ).strip()

        if not url:

            reveal(
                "No URL entered.",
                color=C.RED
            )
            continue

        try:

            if choice == "1":
                action_video(url)

            elif choice == "2":
                action_audio(url)

            elif choice == "3":
                action_best(url)

            elif choice == "4":
                action_show(url)

        except KeyboardInterrupt:

            reveal(
                "\nCancelled.",
                color=C.YELLOW
            )

        except Exception as e:

            reveal(
                f"Error: {e}",
                color=C.RED
            )

        input(
            f"\n{C.DIM}Press Enter to return to menu...{C.RESET}"
        )


# ─────────────────────────── main ─────────────────────────

def main():

    clear()

    show_banner()

    time.sleep(0.3)

    ensure_folder()

    time.sleep(0.3)

    interactive_mode()


if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:

        print(
            f"\n{C.YELLOW}{C.BOLD}Exiting...{C.RESET}"
  )
