#!/bin/sh
# Start Xvfb for headless OpenGL (used by DH_live video rendering)
if [ -z "$DISPLAY" ]; then
    Xvfb :99 -screen 0 1024x768x24 -ac -nolisten tcp &
    export DISPLAY=:99
fi
exec uvicorn server:app --host 0.0.0.0 --port 8000
