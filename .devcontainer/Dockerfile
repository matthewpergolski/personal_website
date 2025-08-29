# Python base image
FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    docker.io \
    ffmpeg \
    libportaudio2 \
    espeak \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# pip installs
RUN pip install --upgrade pip && \
    pip install --upgrade uv

# Set working directory
WORKDIR /workspaces/vscode

# Create vscode user
RUN echo "vscode ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/vscode \
    && chmod 0440 /etc/sudoers.d/vscode \
    && mkdir -p /workspaces/project \
    # Ensure the parent /workspaces directory exists and is owned correctly before chown'ing subdirs
    && mkdir -p /workspaces \
    && chown -R vscode:vscode /workspaces

# Python alias
RUN echo 'alias python="/user/bin/python3.12"' >> /home/vscode/.bashrc

WORKDIR /workspaces/project