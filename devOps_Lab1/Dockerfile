# ============================================================
# Dockerfile — DevOps Lab 1: OpenAI API in Python
# ============================================================
# This file tells Docker how to package our Python script so
# it can run inside an isolated container on any machine.
# ============================================================

# --- Stage 1: Choose a base image ---
# We use the official Python 3.11 "slim" variant.
# "slim" means fewer pre-installed packages → smaller final image.
FROM python:3.11-slim

# --- Stage 2: Set the working directory inside the container ---
# All subsequent commands will run from /app.
WORKDIR /app

# --- Stage 3: Copy dependency list first (layer-cache trick) ---
# Docker builds in layers. Copying requirements.txt first lets Docker
# re-use the cached "pip install" layer as long as this file hasn't changed,
# which speeds up re-builds when you only edit Python source files.
COPY requirements.txt .

# --- Stage 4: Install Python dependencies ---
# --no-cache-dir keeps the image smaller (no pip download cache stored).
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 5: Copy the rest of the source code ---
COPY . .

# --- Stage 6: Security — do NOT bake secrets into the image ---
# The OPENAI_API_KEY must be injected at runtime via an environment variable:
#   docker run -e OPENAI_API_KEY=sk-... <image>
# Defining it here as empty makes the requirement explicit without storing a value.
ENV OPENAI_API_KEY=""

# --- Stage 7: Default command ---
# When someone runs the container, Python executes main.py.
CMD ["python", "main.py"]
