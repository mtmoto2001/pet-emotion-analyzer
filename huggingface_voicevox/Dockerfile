FROM voicevox/voicevox_engine:cpu-ubuntu20.04-latest

# Switch to root to install dependencies
USER root

# Set UTF-8 environment variables for Python
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install pip and clean up apt cache to keep image small
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages for the proxy using pip3
RUN pip3 install --no-cache-dir fastapi uvicorn[standard] httpx

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

EXPOSE 7860

CMD ["/bin/bash", "/opt/start.sh"]
