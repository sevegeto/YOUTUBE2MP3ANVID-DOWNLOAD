YouTube Downloader Pro — Program Description
YouTube Downloader Pro is a cross-platform command-line tool written in Python that downloads videos and audio from YouTube and other yt-dlp–supported sites. It runs natively on Windows 11 and Fedora 44, automatically adapting its behavior to the operating system it detects.

Core Functionality
Video downloads in MP4, with selectable quality: Best available, 1080p, 720p, 480p, 360p, or lowest. Video and audio streams are fetched separately at maximum quality and merged automatically via FFmpeg.

Audio-only downloads in MP3 (192 kbps default), M4A, or Opus, with embedded metadata (title, artist, cover art).

Playlist support: when a URL contains a playlist, the user is asked whether to download the entire list or just the single video. Unavailable or deleted videos are skipped silently without interrupting the queue.

Batch processing: multiple URLs can be entered in one session, processed sequentially.

Audio Normalization
Every downloaded audio file is automatically processed with FFmpeg's loudnorm filter using a dual-pass approach — first measuring, then applying correction. The target is -16 LUFS (Integrated), -1.5 dB True Peak, and LRA 11 dB, matching the standards used by YouTube, Spotify, and Apple Music. This guarantees consistent perceived volume across all tracks, ideal for voice recordings, podcasts, or music libraries.

Smart Organization
Files are stored in two separate subfolders — videos/ and audio/ — under a common base directory. A download archive (.historial/descargados_video.txt and descargados_audio.txt) tracks every video ID already downloaded, so re-running the script on the same playlist only fetches new content.

Automatic Cookies
The script detects the browser installed on the system (Firefox, Chrome, Edge, Brave, Chromium, Opera) and extracts its YouTube session cookies automatically via yt-dlp's cookiesfrombrowser. This bypasses most "Sign in to confirm you're not a bot" prompts without requiring any manual cookie export.

Desktop Integration
On first run, the script offers to create a desktop shortcut — a .lnk file on Windows (via pywin32) or a .desktop launcher on Fedora (with a menu entry under ~/.local/share/applications/). The shortcut launches the script directly with a single click.

Notifications & Logging
When all downloads finish, a native desktop notification is shown: a Windows Toast (via PowerShell) or a notify-send popup on Fedora, reporting the number of files and total time. Errors are recorded in errores.log with timestamp and severity, without stopping the batch.

Additional Features
Automatic detection of a JavaScript runtime (Deno, Node, or Bun) to avoid YouTube extraction warnings.

Configurable retries, socket timeouts, and Windows-safe filename sanitization.

Real-time progress bar with percentage, download speed, and ETA.

Clean cancellation via Ctrl+C.

All major parameters (bitrate, LUFS target, cookie usage, notification toggle, etc.) centralized in a single CONFIG dictionary at the top of the script.

Technical Stack
Python 3.10+ · yt-dlp · FFmpeg · reportlab (for PDF manuals) · pywin32 + winshell (Windows shortcut) · notify-send / PowerShell Toast (notifications).
