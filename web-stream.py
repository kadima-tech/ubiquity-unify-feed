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
CAMERA_URL = "http://192.168.2.135/snap.jpeg"
UPDATE_INTERVAL = 2.0  # seconds

# Authentication cookie from environment variable
AUTH_COOKIE = os.getenv('UNIFI_AUTH_COOKIE')
if not AUTH_COOKIE:
    raise ValueError("UNIFI_AUTH_COOKIE environment variable is not set")

# Browser-like headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'image/jpeg,*/*'
}

# Global variables for thread-safe image handling
current_frame = None
frame_lock = Lock()

def get_camera_frame():
    """Fetch a single frame from the camera"""
    try:
        # Add timestamp to prevent caching
        params = {'cb': str(int(time.time()))}
        
        # Fetch image with cookies and headers
        response = requests.get(CAMERA_URL, 
                            params=params,
                            headers=headers,
                            cookies={'authId': AUTH_COOKIE, 'ubntActiveUser': 'true'})
        response.raise_for_status()
        
        # Return the raw JPEG data
        return response.content
    except Exception as e:
        logging.error(f"Error fetching frame: {e}")
        return None

def frame_updater():
    """Background thread function to continuously update frames"""
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
        time.sleep(0.1)  # Short sleep to prevent CPU overuse

def generate_frames():
    """Generator function for streaming frames"""
    while True:
        with frame_lock:
            if current_frame is not None:
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n')
        time.sleep(0.1)  # Short sleep to prevent CPU overuse

@app.route('/')
def index():
    """Serve the main page with the video stream"""
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
    """Route for the video feed"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Start the frame updater thread
    updater_thread = Thread(target=frame_updater, daemon=True)
    updater_thread.start()
    
    # Run the Flask app
    print("\nStarting web server...")
    print("Access the stream at: http://localhost:8000")
    print("To access from other devices, use your computer's IP address instead of localhost")
    app.run(host='0.0.0.0', port=8000, debug=False) 