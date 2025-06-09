from pathlib import Path
from urllib.parse import urlparse
import datetime
from yt_dlp import YoutubeDL
from yt_dlp.networking.impersonate import ImpersonateTarget
import appdata


def move_to_onedrive():
    print("Onedrive not implemented yet.")


def move_to_3b():
    print("3b not implemented yet.")


output_options = {"local": "./vids", "onedrive": move_to_onedrive, "3b": move_to_3b}


# class DLLogger:
#     def __init__(self, error_log: str) -> None:
#         self.error_log = error_log

#     def debug(self, msg: str) -> None:
#         if msg.startswith("[debug]"):
#             pass
#         else:
#             self.info(msg)

#     def info(self, msg: str) -> None:
#         pass

#     def warning(self, msg: str) -> None:
#         pass

#     def error(self, msg: str) -> None:
#         print(msg)
#         with open(self.error_log, "a", encoding="utf-8") as f:
#             f.write(f"{datetime.datetime.now()} - {msg}\n")


class DL:
    def __init__(self, urls: list[str], output_option: str, run_as_test: bool) -> None:
        self._ignore_errors = "only_download"
        self._local_storage = "./vids"

        self.urls = urls
        self.output_option = output_option
        self.run_as_test = run_as_test
        self.appsettings: dict = appdata.get_appsettings()
        self.ffmpeg_path = self._get_ffmpeg_path()

    def download_video(self) -> None:
        print(f"{datetime.datetime.now()} - Stating downloads...")

        if self.run_as_test:
            self._dl_test(self.urls, self.output_option)
            return

        non_standard_urls = self._handle_non_standard_urls(self.urls)
        standard_urls = [u for u in self.urls if u not in non_standard_urls]
        if standard_urls:
            print(f"\n{datetime.datetime.now()} - Running standard extractor urls")
            self.dl_vids_w_options(standard_urls, self._get_dl_options())

        print(f"\n{datetime.datetime.now()} - Finished attempting urls")

    def dl_vids_w_options(self, urls: list[str], options: dict) -> None:
        with YoutubeDL(options) as ydl:
            try:
                ydl.download(urls)
                # output_options[output_option]()

            except Exception as e:
                print(f"{datetime.datetime.now()} - An processing error occurred: {e}")

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
            # "logger": DLLogger(self.appsettings["error_log"]),
        }
        return opts

    def _handle_non_standard_urls(self, urls: list[str]) -> list[str]:
        print("Handling non-standard URLs...")

        def get_forced_generic_options() -> dict:
            optns = self._get_dl_options()
            optns["force_generic_extractor"] = ["generic", "default"]
            return optns

        def get_simple_impersonate_options() -> dict:
            optns = self._get_dl_options()
            optns["impersonate"] = ImpersonateTarget(client="edge", os="windows")
            return optns
        
        def get_simple_cookie_options() -> dict:
            optns = self._get_dl_options()
            tuple_parts = self.appsettings["cookie_templates"]["generic"]
            optns["cookiesfrombrowser"] = tuple([None if p == "" else p for p in tuple_parts])
            return optns

        special_cases = {
            "forced_generic_sites": get_forced_generic_options,
            "simple_impersonate_sites": get_simple_impersonate_options,
            "cookie_sites": get_simple_cookie_options,
        }
        handled_urls = []

        for special_case in special_cases.keys():
            special_urls = [
                u
                for u in self.urls
                if urlparse(u).netloc in self.appsettings[special_case]
            ]

            if special_urls:
                print(f"\n{datetime.datetime.now()} - Running {special_case} urls")
                handled_urls += special_urls
                options = special_cases[special_case]()
                self.dl_vids_w_options(special_urls, options)

        return handled_urls

    def _dl_test(self, urls: list[str], output_option: str) -> None:
        for url in urls:
            print(f"url={url} --- output_path=./vids")

        print(f"output_option={output_option}")
