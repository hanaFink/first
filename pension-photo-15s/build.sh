#!/usr/bin/env bash
# Builds pension-net-vs-gross-photo-15s.mp4 (1080x1920, 30fps, 15s) from the four stills in images/
# Requires: node + playwright (Chromium), python3, ffmpeg
set -euo pipefail
cd "$(dirname "$0")"
WORK="${WORK:-$(mktemp -d)}"

NODE_PATH="${NODE_PATH:-$(npm root -g)}" node render.js "$WORK/frames" 30 15
python3 audio.py "$WORK/soundtrack.wav"

ffmpeg -y -loglevel error -framerate 30 -i "$WORK/frames/%04d.png" -i "$WORK/soundtrack.wav" \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -profile:v high -r 30 \
  -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart \
  pension-net-vs-gross-photo-15s.mp4

echo "done: $(pwd)/pension-net-vs-gross-photo-15s.mp4"
