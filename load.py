import os
import tempfile
import yt_dlp


def video_load(url, quality):
    tmp_dir = tempfile.mkdtemp(prefix="video_")

    options = {
        "format": f"bestvideo[height<={quality}]+bestaudio/best",
        "outtmpl": os.path.join(tmp_dir, "%(id)s.%(ext)s"),
        "merge_output_format": "mp4",
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)

    video_id = info["id"]
    title = info["title"]
    video_file = os.path.join(tmp_dir, f"{video_id}.mp4")

    print(video_file)
    return video_file, title


def audio_load(url):
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
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)

    audio_id = info["id"]
    title = info["title"]
    audio_file = os.path.join(temp_dir, f"{audio_id}.mp3")

    print(audio_file)
    return audio_file, title
