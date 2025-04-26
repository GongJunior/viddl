import argparse
import dllib


def add_dl_args(subparser: argparse._SubParsersAction) -> None:
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


def add_mv_args(subparser: argparse._SubParsersAction) -> None:
    parser = subparser.add_parser(
        "mv", help="Move downloaded videos to a specified location"
    )
    parser.add_argument(
        "-s",
        "--source",
        type=str,
        required=True,
        help="Source path of the downloaded video",
    )
    parser.add_argument(
        "-d",
        "--destination",
        type=str,
        required=True,
        choices=dllib.output_options.keys(),
        help="Destination path for the video.",
    )


def run_cli(args: list) -> None:
    parser = argparse.ArgumentParser(
        prog="video_downloader",
        description="CLI for handling video downloads and storing.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_dl_args(subparsers)
    add_mv_args(subparsers)

    namespace = parser.parse_args(args)

    match namespace.command:
        case "dl":
            dllib.DL(namespace.urls, namespace.output, namespace.test).download_video()
        case "mv":
            print(f"Moving from {namespace.from_path} to {namespace.to_path}")
        case _:
            parser.print_help()
            exit(1)
