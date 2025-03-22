#!/usr/bin/env python3
"""
AprilTag Detection System - Main Application
Combines backend detection with Flask frontend
"""
from flask import Flask, render_template, Response
import threading
import time
import os

from backend.camera_manager import CameraManager
from backend.apriltag_detector import AprilTagDetector
from backend.frame_processor import FrameProcessor

# Create Flask application
app = Flask(__name__, 
            static_folder='frontend/static',
            template_folder='frontend/templates')

# Initialize components
camera = CameraManager(resolution=(640, 640))
detector = AprilTagDetector()
processor = FrameProcessor(camera, detector)

# Start camera and processing in separate thread
def start_background_processing():
    camera.start_camera()
    print("Camera started successfully")
    print(f"Detecting AprilTags - Family: {detector.get_family()}")
    processor.start_processing()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Return the video feed as a multipart response"""
    return Response(processor.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stats')
def stats():
    """Return detection statistics as JSON"""
    return processor.get_stats()

if __name__ == '__main__':
    # Start camera and processing in background thread
    processing_thread = threading.Thread(target=start_background_processing)
    processing_thread.daemon = True
    processing_thread.start()
    
    # Allow time for camera to initialize
    time.sleep(2)
    
    # Start Flask server
    print("Starting web server at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)
