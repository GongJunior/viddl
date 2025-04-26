from pathlib import Path
from urllib.parse import urlparse
import json
import datetime
from yt_dlp import YoutubeDL


def move_to_onedrive():
    print("Onedrive not implemented yet.")


def move_to_3b():
    print("3b not implemented yet.")


output_options = {"local": "./vids", "onedrive": move_to_onedrive, "3b": move_to_3b}


class DL:
    def __init__(self, urls: list[str], output_option: str, run_as_test: bool) -> None:
        self._ignore_errors = "only_download"
        self._local_storage = "./vids"

        self.urls = urls
        self.output_option = output_option
        self.run_as_test = run_as_test
        self.appsettings: dict = self._get_appsettings()
        self.ffmpeg_path = self._get_ffmpeg_path()

    def download_video(self) -> None:
        print(f"{datetime.datetime.now()} - Stating downloads...")

        if self.run_as_test:
            self._dl_test(self.urls, self.output_option)
            return

        generic_required_urls = [
            u
            for u in self.urls
            if urlparse(u).netloc in self.appsettings["forced_generic_sites"]
        ]
        if generic_required_urls:
            print(f"{datetime.datetime.now()} - Running generic extractor urls")
            options = self._get_dl_options()
            options["force_generic_extractor"] = ["generic", "default"]
            self.dl_vids_w_options(generic_required_urls, options)

        standard_urls = [u for u in self.urls if u not in generic_required_urls]
        if standard_urls:
            print(f"{datetime.datetime.now()} - Running standard extractor urls")
            self.dl_vids_w_options(standard_urls, self._get_dl_options())

    def dl_vids_w_options(self, urls: list[str], options: dict) -> None:
        with YoutubeDL(options) as ydl:
            try:
                ydl.download(urls)
                print(
                    f"{'Videos' if len(urls) > 1 else 'Video'} downloaded successfully."
                )

                # output_options[output_option]()

            except Exception as e:
                print(
                    f"{datetime.datetime.now()} - An post-processing error occurred: {e}"
                )

    def _get_appsettings(self) -> dict:
        with open("./secrets/appsettings.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

    def _get_ffmpeg_path(self) -> str:
        expected_files = set(["ffmpeg.exe", "ffplay.exe", "ffprobe.exe"])

        path = self.appsettings.get("ffmpg")

        if path is None:
            raise ValueError("ffmpeg_path not found in appsettings.json")

        found_files = set([f.name for f in Path(path).iterdir() if f.is_file()])
        if not expected_files == found_files:
            raise ValueError("ffmpeg_path does not contain the expected files")

        return path

    def _get_dl_options(self) -> dict:
        opts = {
            "ignoreerrors": self._ignore_errors,
            "paths": {"home": self._local_storage},
            "ffmpeg_location": self.ffmpeg_path,
        }
        return opts

    def _dl_test(self, urls: list[str], output_option: str) -> None:
        for url in urls:
            print(f"url={url} --- output_path=./vids")

        print(f"output_option={output_option}")
