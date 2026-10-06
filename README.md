# Just One More — animated vertical short

The finished deliverable is **[artifacts/video.mp4](artifacts/video.mp4)**.

See [production notes, research, specifications and limitations](artifacts/README.md), the [final-frame contact sheet](artifacts/contact-sheet.jpg), and [technical check results](artifacts/checks.txt).

Original artwork and an original synthesized score; 30 seconds, 720 × 1280, 30 fps, H.264 video with AAC stereo audio.

Rebuild offline with `python3 src/make_video.py`; verify with `python3 src/check_video.py`. Requires Python 3.12/Linux x86_64 and system ffmpeg/ffprobe. Pillow is included as ordinary files in `vendor/`, along with its bundled-library licenses; font licensing is in `assets/FONT-LICENSE.txt`.
