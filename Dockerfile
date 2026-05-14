FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY web-stream.py .

# Credentials and controller URL (override at runtime)
ENV UNIFI_BASE_URL="http://192.168.2.135"
ENV UNIFI_USERNAME="ubnt"
ENV UNIFI_PASSWORD="ubnt"

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "web-stream.py"] 