import os
import tempfile
import yt_dlp
AUDIO_LIMIT = 1000 * 1024 * 1024


def audio_progress_hook(d):
    if d["status"] == "downloading":
        downloaded = d.get("downloaded_bytes", 0)
        if downloaded > AUDIO_LIMIT:
            raise Exception


def audio_download(url):
    temp_dir = tempfile.mkdtemp(prefix="audio_")

    options = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "progress_hooks": [audio_progress_hook],
    }
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)

        audio_id = info["id"]
        title = info["title"]
        audio_file = os.path.join(temp_dir, f"{audio_id}.mp3")

        return audio_file, title
    except Exception:
        return False

def audio_cheker(url):
    check_options = {
        "format": "bestaudio/best",
        "quiet": True, }

    with yt_dlp.YoutubeDL(check_options) as ydl:
        info = ydl.extract_info(url, download=False)

    size = info.get("filesize") or info.get("filesize_approx")

    print(size)
    if size is None or size <= AUDIO_LIMIT:
        return audio_download(url)
    else:
        return False



