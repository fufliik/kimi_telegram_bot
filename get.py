import yt_dlp


def get_qualities_video(url):
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        qualities_set = set()

        for f in info.get("formats", []):
            height = f.get("height")

            if height in {1080, 720, 480, 360}:
                qualities_set.add(height)

        if not qualities_set:
            return None

        return sorted(qualities_set, reverse=True)
    except Exception:
        return None


