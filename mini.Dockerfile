FROM ghcr.io/astral-sh/uv:python3.14-alpine

RUN apk update && apk upgrade
RUN apk add deno
WORKDIR /ffmpeg
RUN wget -o /tmp/ffmpeg-dl.log \
    -O ffmpeg.tar.xz \
    https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz
RUN tar -xvJf ffmpeg.tar.xz --strip-components=1 && rm ffmpeg.tar.xz

COPY . /app
COPY ./secrets/appsettings_prod.json /app/secrets/appsettings.json
WORKDIR /app
ENV UV_NO_DEV=1
RUN uv sync --locked
CMD [ "uv", "run", "/app/api.py" ]