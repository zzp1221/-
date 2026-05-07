#!/bin/sh
set -e

AVATAR_DATA_DIR="${AVATAR_DATA_DIR:-/data/sandbox-temp/avatar_data}"
DEFAULT_AVATAR_VIDEO="${DEFAULT_AVATAR_VIDEO:-/app/src/ai_modules/generation/dh_live/video_data/default_avatar.mp4}"
AVATAR_ASSET_MARKER="$AVATAR_DATA_DIR/assets/combined_data.json.gz"
PREBUILT_AVATAR_ASSETS_DIR="${PREBUILT_AVATAR_ASSETS_DIR:-/opt/dh_live_static/assets}"

# Start Xvfb for headless OpenGL (used by DH_live video rendering)
if [ -z "$DISPLAY" ]; then
    Xvfb :99 -screen 0 1024x768x24 -ac -nolisten tcp &
    export DISPLAY=:99
fi

if [ ! -f "$AVATAR_ASSET_MARKER" ]; then
    mkdir -p "$AVATAR_DATA_DIR"
    if [ -f "$PREBUILT_AVATAR_ASSETS_DIR/combined_data.json.gz" ]; then
        echo "Avatar assets missing, seeding prebuilt DH_live assets..."
        rm -rf "$AVATAR_DATA_DIR/assets"
        cp -R "$PREBUILT_AVATAR_ASSETS_DIR" "$AVATAR_DATA_DIR/assets"
    else
        echo "Avatar assets missing, preprocessing default avatar..."
        python scripts/preprocess_avatar.py --input "$DEFAULT_AVATAR_VIDEO" --output "$AVATAR_DATA_DIR"
    fi
fi

exec uvicorn server:app --host 0.0.0.0 --port 8000
