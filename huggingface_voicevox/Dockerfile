FROM voicevox/voicevox_engine:cpu-ubuntu20.04-latest

# Switch to root to install dependencies
USER root

# Set UTF-8 environment variables for Python
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install Python packages for the proxy and engine using the embedded Python environment
RUN /opt/python/bin/python3 -m pip install --no-cache-dir fastapi uvicorn[standard] httpx


# Copy application files
COPY app.py /opt/app.py
COPY start.sh /opt/start.sh

# Make start script executable
RUN chmod +x /opt/start.sh

# HF Spaces may run as non-root (uid 1000), ensure necessary permissions
RUN mkdir -p /tmp/voicevox_cache && \
    chmod -R 777 /tmp/voicevox_cache && \
    chmod -R 777 /opt

# Set the working directory to VOICEVOX engine location
WORKDIR /opt/voicevox_engine

# Switch back to non-root user for Hugging Face Spaces (UID 1000)
USER 1000

EXPOSE 7860

CMD ["/bin/bash", "/opt/start.sh"]

