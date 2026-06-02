#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/david/Desktop/1NST4-CH3K"
DISPLAY_NUM=99
WIDTH=1280
HEIGHT=720
FPS=15
SECONDS_CAPTURE=20
OUT_DIR="$ROOT/usage-recordings"
OUT_MP4="$OUT_DIR/demo_usage_recording.mp4"
OUT_GIF="$OUT_DIR/demo_usage_recording.gif"

mkdir -p "$OUT_DIR"

# Start virtual display
Xvfb :$DISPLAY_NUM -screen 0 ${WIDTH}x${HEIGHT}x24 >"$OUT_DIR/xvfb.log" 2>&1 &
XVFB_PID=$!
export DISPLAY=:$DISPLAY_NUM

cleanup() {
  kill "$XTERM_PID" >/dev/null 2>&1 || true
  kill "$FFMPEG_PID" >/dev/null 2>&1 || true
  kill "$XVFB_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Launch terminal demo
xterm -geometry 120x40 -fa 'Monospace' -fs 14 -e bash -lc "cd '$ROOT' && uv run python demo_validation.py" >/dev/null 2>&1 &
XTERM_PID=$!

# Give UI time to paint
sleep 1

ffmpeg -y -f x11grab -video_size ${WIDTH}x${HEIGHT} -framerate $FPS -i :$DISPLAY_NUM -t $SECONDS_CAPTURE \
  -c:v libx264 -preset veryfast -pix_fmt yuv420p "$OUT_MP4" >/tmp/demo_ffmpeg.log 2>&1 &
FFMPEG_PID=$!

wait "$XTERM_PID"
sleep 1
kill "$FFMPEG_PID" >/dev/null 2>&1 || true
wait "$FFMPEG_PID" || true

# Create GIF preview
ffmpeg -y -i "$OUT_MP4" -vf "fps=10,scale=960:-1:flags=lanczos" "$OUT_GIF" >/tmp/demo_ffmpeg_gif.log 2>&1

echo "[demo] recording complete: $OUT_MP4"
echo "[demo] gif complete: $OUT_GIF"
