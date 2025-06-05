import argparse
from dataclasses import dataclass
import sys
import dllib
import appdata

@dataclass
class NamespaceHolder(argparse.Namespace):
    command: str
    urls: list[str]
    output: str
    test: bool
    import_data: str
    privacy: int
    search: str
    disk: bool


def handle_data_results(namespace_obj) -> None:
    pass

def add_dl_args(subparser: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparser.add_parser("dl", help="Download videos from the given URL(s)")
    parser.add_argument(
        "-u",
        "--urls",
        type=str,
        required=True,
        nargs="+",
        help="URL of the video to download",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        choices=dllib.output_options.keys(),
        default="local",
        help="Output path for the downloaded video.",
    )

    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Test the download without actually downloading it.",
    )
    return parser


def add_data_args(subparser: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparser.add_parser(
        "data", help="Manage video data after download"
    )
    parser.add_argument(
        "-i",
        "--import",
        dest="import_data",
        type=str,
        required=False,
        nargs="+",
        help="Import video to app for tracking",
    )
    parser.add_argument(
        "-p",
        "--privacy",
        type=int,
        required=False,
        default=3,
        help="Privacy level for the video (1-3)",
    )
    parser.add_argument(
        "-s",
        "--search",
        type=str,
        required=False,
        help="Search for a video by its server name, accepts * as wildcard",
    )
    parser.add_argument(
        "-d",
        "--disk",
        action="store_true",
        help="Check if the video is on disk",
    )
    # show stats of tracked videos
    parser.add_argument(
        "-st",
        "--stats",
        action="store_true",
        help="Show statistics of tracked videos",
    )

    return parser


def run_cli(args: list) -> None:
    parser = argparse.ArgumentParser(
        prog="video_downloader",
        description="CLI for handling video downloads and storing.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    dl_parser = add_dl_args(subparsers)
    data_parser = add_data_args(subparsers)

    namespace: NamespaceHolder = parser.parse_args(args) # type: ignore

    match namespace.command:
        case "dl":
            dllib.DL(namespace.urls, namespace.output, namespace.test).download_video()
        case "data":
            if namespace.import_data:
                _ = [
                    print(appdata.import_vid_details(result, namespace.privacy)) 
                    for result 
                    in namespace.import_data]
                return
            if namespace.search:
                print(f"Searching for video: {namespace.search}")
                return
            data_parser.print_help()
        case _:
            parser.print_help()
            exit(1)
