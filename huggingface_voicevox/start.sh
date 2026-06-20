#!/bin/bash
set -e

# Ensure we are in the correct directory
cd /opt/voicevox_engine

echo "=== Listing files in /opt/python/bin ==="
ls -la /opt/python/bin || echo "No /opt/python/bin"

echo "=== Python path and environment info ==="
/opt/python/bin/python3 -c "import sys; print('sys.path:', sys.path)"
/opt/python/bin/python3 -m pip list || echo "pip list failed"
find /opt/python -name "uvicorn*" || echo "uvicorn not found in /opt/python"

echo "=== Starting VOICEVOX Engine on port 50021 ==="
# Start VOICEVOX engine in the background using the embedded Python environment
/opt/python/bin/python3 run.py --host 127.0.0.1 --port 50021 --cpu_num_threads 2 &


# Wait for VOICEVOX engine to become ready (max 120 seconds)
echo "=== Waiting for VOICEVOX Engine to be ready ==="
MAX_WAIT=120
ELAPSED=0
INTERVAL=2

while [ $ELAPSED -lt $MAX_WAIT ]; do
    if curl -s http://127.0.0.1:50021/version > /dev/null 2>&1; then
        echo "=== VOICEVOX Engine is ready! ==="
        break
    fi
    echo "  Waiting... (${ELAPSED}s / ${MAX_WAIT}s)"
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo "ERROR: VOICEVOX Engine failed to start within ${MAX_WAIT} seconds"
    exit 1
fi

echo "=== Starting FastAPI Proxy on port 7860 ==="
exec /opt/python/bin/python3 -m uvicorn app:app --host 0.0.0.0 --port 7860 --app-dir /opt

