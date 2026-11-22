FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

# Install OS dependencies
RUN apt update && apt upgrade -y
RUN apt install -y curl unzip
RUN curl -fsSL https://deno.land/install.sh | sh
WORKDIR /ffmpeg
RUN wget -o /tmp/ffmpeg-dl.log \
    -O ffmpeg.tar.xz \
    https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz
RUN tar -xvJf ffmpeg.tar.xz --strip-components=1 && rm ffmpeg.tar.xz

# Application setup
COPY . /app
COPY ./secrets/appsettings_prod.json /app/secrets/appsettings.json
WORKDIR /app
ENV UV_NO_DEV=1
RUN uv sync --locked
CMD [ "uv", "run", "fastapi", "run", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "/app/api.py" ]