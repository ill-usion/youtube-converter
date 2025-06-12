import os
from urllib.parse import unquote
from flask import Flask, request, render_template
from yt_dlp.YoutubeDL import YoutubeDL
from functools import lru_cache

TEMPLATE_FOLDER = "./public"
STATIC_FOLDER = "./public/static"

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)

@app.route("/")
def index():
    return render_template("index.html")

@lru_cache
def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        best_audio = max(
        (f for f in info.get("formats", []) if f.get("vcodec") == "none"),
        key=lambda f: f.get("abr", 0) or 0,
        default=None
    )

    estimated_mp3_bitrate = best_audio.get("abr") if best_audio else 128

    return {
        "id": info.get("id"),
        "title": info.get("title"),
        "artist": info.get("artist") or info.get("uploader"),
        "album": info.get("album") or info.get("title"),
        "uploader": info.get("uploader"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "upload_date": info.get("upload_date"),
        "view_count": info.get("view_count"),
        "like_count": info.get("like_count"),
        "average_rating": info.get("average_rating"),
        "webpage_url": info.get("webpage_url"),
        "audio_format_source": {
            "format_id": best_audio.get("format_id") if best_audio else None,
            "ext": best_audio.get("ext") if best_audio else None,
            "acodec": best_audio.get("acodec") if best_audio else None,
            "abr": best_audio.get("abr") if best_audio else None,
        },
        "estimated_mp3_bitrate_kbps": estimated_mp3_bitrate
    }

def download_mp3(
    url: str,
    output_dir: str = ".",
    title: str = None,
    artist: str = None,
    album: str = None,
    bitrate: int = 192
) -> str:
    filename_base = title or "output"
    filename_base = "".join(c for c in filename_base if c.isalnum() or c in " _-").rstrip()
    output_path = os.path.join(STATIC_FOLDER, output_dir, f"{filename_base}.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(STATIC_FOLDER, output_dir, '%(id)s.%(ext)s'),
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': str(bitrate),
        }],
        'postprocessor_args': [
            '-metadata', f'title={title or ""}',
            '-metadata', f'artist={artist or ""}',
            '-metadata', f'album={album or ""}',
        ],
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        downloaded_filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + ".mp3"

    if os.path.exists(downloaded_filename):
        os.rename(downloaded_filename, output_path)
        return output_path.removeprefix(TEMPLATE_FOLDER)

    return "Failed to convert.", 500
    
@app.route("/search")
def search():
    url = request.args.get("url")
    if not url:
        return "Missing URL", 400
    
    return get_video_info(url)
    

@app.route('/convert')
def convert():
    url = request.args.get("url")
    if not url:
        return "Missing URL", 400

    info = get_video_info(url)
    return download_mp3(url, 
        "download", 
        info.get("title"), 
        info.get("artist"), 
        info.get("album")
    )

@app.route("/keep-alive")
def keep_alive():
    return '', 204


if __name__ == "__main__":
    app.run(debug=True, port=4040)