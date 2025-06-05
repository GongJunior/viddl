import subprocess
import json
import re
import time
import uuid
from typing import Optional
from pathlib import Path
from dataclasses import dataclass

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import Session
from sqlalchemy import Engine, String, Float, Text
from sqlalchemy import select, and_


class Base(DeclarativeBase):
    pass


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    raw_name: Mapped[str] = mapped_column(String(255))
    server_name: Mapped[str] = mapped_column(String(255))
    storage_name: Mapped[str] = mapped_column(String(255))
    is_uploaded: Mapped[bool] = mapped_column(default=False)
    size: Mapped[int] = mapped_column()
    width: Mapped[Optional[int]] = mapped_column()
    height: Mapped[Optional[int]] = mapped_column()
    duration: Mapped[Optional[float]] = mapped_column(Float(2))
    privacy_level: Mapped[int] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, server_name={self.server_name}, size={self.size}, duration={self.duration}, privacy_level={self.privacy_level})>"


@dataclass
class ImportResult:
    new_videos: list[Video]
    duplicate_videos: list[Video]
    error_filenames: Optional[list[str]] = None
    def __str__(self) -> str:
        error_info = "No errors"
        if self.error_filenames:
            error_info = "\n".join(self.error_filenames)
        return f"ImportResult(new_videos={len(self.new_videos)}, duplicate_videos={len(self.duplicate_videos)})\nError files: {error_info}"


def get_appsettings() -> dict:
    with open("./secrets/appsettings.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data


def get_db(with_echo: bool = False) -> Engine:
    from sqlalchemy import create_engine

    connection_string_memory = "sqlite:///:memory:"
    connection_string = get_appsettings().get("connection_string", connection_string_memory)
    if connection_string == connection_string_memory:
        print(
            "Connection string not found in appsettings.json. Using default: sqlite:///:memory:")

#    print(f"Connection string: {connection_string}")
    db = create_engine(connection_string, echo=with_echo)
    return db


def extract_video_info(
    ffprobe_result: dict, probe_file: Path, privacy_level: int = 3
) -> Video:
    vid_stream_info = [
        s for s in ffprobe_result.get("streams", []) if s.get("codec_type") == "video"
    ][0]
    interpreted_time = time.strptime(
        ffprobe_result.get("format", {}).get("duration", "0:0:0.0"), "%H:%M:%S.%f"
    )

    raw_name = probe_file.name
    server_name = re.sub(r"[^a-z0-9._-]", "", raw_name.replace(" ", "_").lower())
    storage_name = str(uuid.uuid4()) + probe_file.suffix
    size = probe_file.stat().st_size
    width = int(vid_stream_info.get("width", 0))
    height = int(vid_stream_info.get("height", 0))
    duration = (
        (interpreted_time.tm_hour * 60)
        + interpreted_time.tm_min
        + (interpreted_time.tm_sec / 100)
    )

    return Video(
        raw_name=raw_name,
        server_name=server_name,
        storage_name=storage_name,
        is_uploaded=False,
        size=size,
        width=width,
        height=height,
        duration=duration,
        privacy_level=privacy_level,
    )


def probe_video_file(file_path: Path, privacy_level: int = 3) -> Video:
    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        "-sexagesimal",
        str(file_path.resolve()),
    ]
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()

    if process.returncode == 0 and stdout:
        # print("Command output:", stdout)
        probe_result = json.loads(stdout)
        return extract_video_info(probe_result, file_path, privacy_level)
    else:
        print(f"Error on {file_path.name}: {stdout} --- {stderr}")
        return Video(raw_name=file_path.name)


def import_vid_details(data_path: str, privacy_level: int = 3, with_echo: bool = False) -> ImportResult:
    print(f"\nImporting video details from {data_path}...")

    accepted_extensions = [".mp4", ".mkv", ".avi", ".mov"]
    raw_videos = []
    path = Path(data_path)

    if not path.exists():
        print(f"Path {data_path} does not exist.")
        return ImportResult([], [])
    if path.is_dir():
        raw_videos = [
            f
            for f in path.iterdir()
            if f.is_file() and f.suffix.lower() in accepted_extensions
        ]
    elif path.is_file() and path.suffix.lower() in accepted_extensions:
        raw_videos = [path]
    if not raw_videos:
        print(f"No valid video files found in {data_path}.")
        return ImportResult([], [])

    videos = [probe_video_file(v, privacy_level) for v in raw_videos]

    db = get_db(with_echo=with_echo)
    with Session(db) as session:
        existing_videos = (
            session.execute(
                select(Video.server_name).where(
                    Video.server_name.in_([v.server_name for v in videos])
                )
            )
            .scalars()
            .all()
        )

        new_videos = []
        duplicate_videos = []
        error_filenames = []
        for video in videos:
            if not video.server_name:
                error_filenames.append(video.raw_name)
                continue
            if video.server_name in existing_videos:
                duplicate_videos.append(video)
                continue
            new_videos.append(video)

        session.add_all(new_videos)
        session.commit()

    return ImportResult(new_videos=new_videos, 
                        duplicate_videos=duplicate_videos,
                        error_filenames=error_filenames)

def search_videos(search_terms: list[str]):
    normalized_terms = [term.strip().lower() for term in search_terms if term.strip()]
    conditions = [Video.server_name.ilike(f"%{term}%") for term in normalized_terms]
    db = get_db(with_echo=True)
    with Session(db) as session:
        query = select(Video).where(and_(*conditions))
        results = session.execute(query).scalars().all()
        return results
