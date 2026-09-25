import os
import tempfile
import yt_dlp
VIDEO_LIMIT = 1000 * 1024 * 1024



def video_get_qualities(url):
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        qualities_set = set()

        for f in info.get("formats", []):
            height = f.get("height")

            if height in {1080, 720, 480, 360}:
                qualities_set.add(height)


        if not qualities_set:
            return False
        return sorted(qualities_set, reverse=True)
    except Exception:
        return False

def video_progress_hook(d):
    if d["status"] == "downloading":
        downloaded = d.get("downloaded_bytes", 0)
        if downloaded > VIDEO_LIMIT:
            raise Exception


def video_download(url, quality):
    tmp_dir = tempfile.mkdtemp(prefix="video_")

    options = {
        "format": f"bestvideo[height<={quality}]+bestaudio/best",
        "outtmpl": os.path.join(tmp_dir, "%(id)s.%(ext)s"),
        "merge_output_format": "mp4",
        "quiet": True,
        "progress_hooks": [video_progress_hook],
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)

        video_id = info["id"]
        title = info["title"]
        video_file = os.path.join(tmp_dir, f"{video_id}.mp4")


        return video_file, title
    except Exception:
        return False

def video_cheker(url, quality):
    options = {
        "format": f"bestvideo[height<={quality}]+bestaudio/best",
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = info.get("requested_formats") or [info]

    size = 0
    for f in formats:
        s = f.get("filesize") or f.get("filesize_approx")
        if s is None:
            size = None
            break
        size += s

    print(size)

    if size is None or size <= VIDEO_LIMIT:
        return video_download(url, quality)
    else:
        return False