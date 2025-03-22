#!/usr/bin/env python3
"""
Camera Manager
Handles camera initialization, configuration, and frame capture
"""
import time
from picamera2 import Picamera2

class CameraManager:
    def __init__(self, resolution=(1280, 720)):
        """
        Initialize the camera with the specified resolution
        
        Args:
            resolution (tuple): Width and height for camera resolution
        """
        self.picam = None
        self.resolution = resolution
        self._init_camera()
        
    def _init_camera(self):
        """Initialize the camera object"""
        try:
            self.picam = Picamera2()
            # Configure camera
            camera_config = self.picam.create_preview_configuration(
                main={"size": self.resolution, "format": "XRGB8888"}
            )
            self.picam.configure(camera_config)
            print("Camera initialized successfully")
        except Exception as e:
            print(f"Error initializing camera: {str(e)}")
            raise
        
    def start_camera(self):
        """Start the camera and give it time to warm up"""
        if self.picam:
            self.picam.start()
            time.sleep(2)  # Warm-up time
            return True
        return False
            
    def stop_camera(self):
        """Stop the camera"""
        if self.picam:
            self.picam.stop()
            
    def capture_frame(self):
        """
        Capture a single frame from the camera
        
        Returns:
            numpy.ndarray: The captured frame or None if an error occurred
        """
        if not self.picam:
            return None
            
        try:
            return self.picam.capture_array()
        except Exception as e:
            print(f"Error capturing frame: {str(e)}")
            return None
