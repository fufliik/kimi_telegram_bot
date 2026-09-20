import yt_dlp


def check_video_size(url, quality):
    options = {
        "format": f"bestvideo[height<={quality}]+bestaudio/best",
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)

    size = sum(
        f.get("filesize") or f.get("filesize_approx") or 0
        for f in info.get("requested_formats", [])
    )

#    if size is None:
#       return None

    return size / 1024 / 1024, size <= 1500 * 1024 * 1024


def check_audio_size(url):
    options = {
        "format": "bestaudio/best",
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)

    size = info.get("filesize") or info.get("filesize_approx")

#    if size is None:
#        return None

    return size / 1024 / 1024, size <= 1500 * 1024 * 1024
