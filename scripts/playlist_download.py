import yt_dlp

def list_videos(playlist_url):
    ydl_opts = {"quiet": True, "extract_flat": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        return [e["url"] for e in info["entries"]]

def download_youtube_as_mp3(url, output_dir="."):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    playlist_link = input("Enter playlist link: ").strip()
    start_index = 1  # download from video 1 onwards
    videos = list_videos(playlist_link)
    total = len(videos)
    print(f"Found {total} videos. Starting from #{start_index}...")

    for i, v in enumerate(videos[start_index - 1:], start=start_index):
        print(f"\n[{i}/{total}] Downloading: {v}")
        try:
            download_youtube_as_mp3(v, output_dir="downloads")
        except Exception as e:
            print(f"❌ Error with video #{i}: {e}")