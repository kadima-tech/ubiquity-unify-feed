from flask import Flask, Response
import cv2
import numpy as np
import requests
import time
from threading import Thread, Lock
import logging
import os

app = Flask(__name__)

# Camera settings
BASE_URL = os.getenv('UNIFI_BASE_URL', 'http://192.168.2.135')
CAMERA_URL = f"{BASE_URL}/snap.jpeg"
LOGIN_URL = f"{BASE_URL}/api/1.1/login"
UPDATE_INTERVAL = 2.0  # seconds

# Credentials from environment variables
UNIFI_USERNAME = os.getenv('UNIFI_USERNAME', 'ubnt')
UNIFI_PASSWORD = os.getenv('UNIFI_PASSWORD', 'ubnt')

# Browser-like headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'image/jpeg,*/*'
}

# Global variables for thread-safe image and auth handling
current_frame = None
frame_lock = Lock()
auth_cookie = None
auth_lock = Lock()


def login():
    """Authenticate with the UniFi controller and return the authId cookie value."""
    try:
        resp = requests.post(
            LOGIN_URL,
            json={'username': UNIFI_USERNAME, 'password': UNIFI_PASSWORD},
            headers={
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
            },
            timeout=10,
        )
        resp.raise_for_status()
        cookie = resp.cookies.get('authId')
        if not cookie:
            logging.error("Login succeeded but no authId cookie in response")
            return None
        logging.info("Successfully logged in to UniFi controller")
        return cookie
    except Exception as e:
        logging.error(f"Login failed: {e}")
        return None


def ensure_auth():
    """Login if we don't have a cookie yet, return True if auth is available."""
    global auth_cookie
    with auth_lock:
        if auth_cookie is None:
            auth_cookie = login()
        return auth_cookie is not None


def refresh_auth():
    """Force a new login, replacing any existing cookie."""
    global auth_cookie
    with auth_lock:
        logging.info("Refreshing auth cookie...")
        auth_cookie = login()
        return auth_cookie is not None


def get_camera_frame():
    """Fetch a single frame from the camera, re-logging in on auth errors."""
    global auth_cookie

    if not ensure_auth():
        return None

    for attempt in range(2):
        with auth_lock:
            cookie = auth_cookie

        try:
            params = {'cb': str(int(time.time()))}
            response = requests.get(
                CAMERA_URL,
                params=params,
                headers=headers,
                cookies={'authId': cookie, 'ubntActiveUser': 'true'},
                timeout=10,
            )

            if response.status_code in (401, 403):
                logging.warning(f"Auth error ({response.status_code}), attempting re-login")
                if attempt == 0 and refresh_auth():
                    continue
                return None

            response.raise_for_status()
            return response.content

        except requests.exceptions.HTTPError:
            return None
        except Exception as e:
            logging.error(f"Error fetching frame: {e}")
            return None

    return None


def frame_updater():
    """Background thread that continuously fetches and caches frames."""
    global current_frame
    last_fetch_time = 0

    while True:
        current_time = time.time()
        if current_time - last_fetch_time >= UPDATE_INTERVAL:
            frame = get_camera_frame()
            if frame is not None:
                with frame_lock:
                    current_frame = frame
            last_fetch_time = current_time
        time.sleep(0.1)


def generate_frames():
    """Generator that yields MJPEG frames for the streaming endpoint."""
    while True:
        with frame_lock:
            if current_frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n')
        time.sleep(0.1)


@app.route('/')
def index():
    """Serve the main page with the video stream."""
    return '''
    <html>
    <head>
        <title>Camera Stream</title>
        <style>
            body {
                margin: 0;
                padding: 20px;
                background: #1a1a1a;
                color: white;
                font-family: Arial, sans-serif;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                text-align: center;
            }
            h1 {
                margin-bottom: 20px;
            }
            img {
                max-width: 100%;
                border-radius: 8px;
                box-shadow: 0 0 20px rgba(0,0,0,0.5);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Live Camera Feed</h1>
            <img src="/video_feed" />
        </div>
    </body>
    </html>
    '''


@app.route('/video_feed')
def video_feed():
    """MJPEG streaming endpoint."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    updater_thread = Thread(target=frame_updater, daemon=True)
    updater_thread.start()

    print("\nStarting web server...")
    print("Access the stream at: http://localhost:8000")
    print("To access from other devices, use your computer's IP address instead of localhost")
    app.run(host='0.0.0.0', port=8000, debug=False)
