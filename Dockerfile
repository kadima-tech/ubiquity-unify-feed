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

# Environment variable for auth (to be provided at runtime)
ENV UNIFI_AUTH_COOKIE=""

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "web-stream.py"] 