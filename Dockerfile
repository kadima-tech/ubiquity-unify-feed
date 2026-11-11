# python:3.15.2-slim
# CPython 3.15.2, tagged 2026-10-25 (includes CVE-2026-115557). Multi-arch index.
FROM python:3.15.2-slim@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY web-stream.py .

# Non-sensitive defaults (pass UNIFI_PASSWORD at runtime, not here)
ENV UNIFI_BASE_URL="http://192.168.2.135"
ENV UNIFI_USERNAME="ubnt"

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "web-stream.py"] 