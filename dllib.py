import shutil
from pathlib import Path
import json
import datetime
from yt_dlp import YoutubeDL

def move_to_onedrive():
    print("Onedrive not implemented yet.")

def move_to_3b():
    print("3b not implemented yet.")

output_options = {
    "local": "./vids",
    "onedrive": move_to_onedrive,
    "3b": move_to_3b
}
def get_ffmpeg_path() -> str:
    expected_files = set(["ffmpeg.exe", "ffplay.exe", "ffprobe.exe"])

    with open("./secrets/appsettings.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        path = data.get("ffmpg")

        if path is None:
            raise ValueError("ffmpeg_path not found in appsettings.json")

        found_files = set([f.name for f in Path(path).iterdir() if f.is_file()])
        if not expected_files == found_files:
            raise ValueError("ffmpeg_path does not contain the expected files")

        return path

def download_video(urls: list[str], output_option: str, run_as_test: bool) -> None:
    print(f"{datetime.datetime.now()} - Stating downloads...")

    if run_as_test:
        dl_test(urls, output_option)
        return

    ydl_opts = {
        "paths": {"home": "./vids"},
        "ffmpeg_location": get_ffmpeg_path(),
        "force_generic_extractor": ["generic", "default"],
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download(urls)
            print(f"{'Videos' if len(urls) > 1 else 'Video'} downloaded successfully.")

            #output_options[output_option]()

        except Exception as e:
            print(f"{datetime.datetime.now()} - An error occurred: {e}")


def dl_test(urls: list[str], output_option: str) -> None:
    for url in urls:
        print(f"url={url} --- output_path=./vids")
    
    print(f"output_option={output_option}")