FROM python:3.9-slim

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