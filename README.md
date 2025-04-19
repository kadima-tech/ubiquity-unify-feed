# Ubiquiti UniFi Camera Feed

A Python web application that streams video feed from a Ubiquiti UniFi camera. This application provides a web interface to view the camera feed in real-time.

## Features

- Real-time video streaming from UniFi camera
- Web interface for viewing the feed
- Configurable update interval
- Thread-safe frame handling
- Authentication support for UniFi cameras

## Requirements

- Python 3.x
- Flask
- OpenCV
- NumPy
- Requests

## Installation

1. Clone the repository:
```bash
git clone git@github.com:kadima-tech/ubiquiti-unifi-feed.git
cd ubiquiti-unifi-feed
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Configuration

1. Set up the environment variable for authentication:
```bash
# Linux/macOS
export UNIFI_AUTH_COOKIE="your-auth-cookie-here"

# Windows (Command Prompt)
set UNIFI_AUTH_COOKIE=your-auth-cookie-here

# Windows (PowerShell)
$env:UNIFI_AUTH_COOKIE="your-auth-cookie-here"
```

2. Update the following variables in `web-stream.py` to match your camera settings:
- `CAMERA_URL`: The URL of your UniFi camera's snapshot endpoint
- `UPDATE_INTERVAL`: The interval between frame updates (in seconds)

## Usage

Run the application:
```bash
python web-stream.py
```

The web interface will be available at `http://localhost:8000`. To access from other devices on your network, use your computer's IP address instead of localhost.

## License

MIT License 