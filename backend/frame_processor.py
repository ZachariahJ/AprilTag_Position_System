#!/usr/bin/env python3
"""
Frame Processor
Processes frames from the camera, detects AprilTags, and generates video stream
"""
import cv2
import time
import threading
import json
from datetime import datetime

class FrameProcessor:
    def __init__(self, camera_manager, apriltag_detector):
        """
        Initialize the frame processor
        
        Args:
            camera_manager: Camera manager instance
            apriltag_detector: AprilTag detector instance
        """
        self.camera = camera_manager
        self.detector = apriltag_detector
        self.processing = False
        
        # For storing the latest processed frame
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
        # For tracking statistics
        self.stats = {
            "tags_detected": 0,
            "processing_fps": 0,
            "last_detection_time": None
        }
        self.stats_lock = threading.Lock()
        self.frame_count = 0
        self.start_time = None
        
    def start_processing(self):
        """Start the frame processing loop in a background thread"""
        if self.processing:
            return
            
        self.processing = True
        self.start_time = time.time()
        
        # Start processing thread
        threading.Thread(target=self._processing_loop, daemon=True).start()
        
    def stop_processing(self):
        """Stop the frame processing loop"""
        self.processing = False
        
    def _processing_loop(self):
        """Main processing loop that runs in a background thread"""
        while self.processing:
            # Get frame from camera
            frame = self.camera.capture_frame()
            if frame is None:
                time.sleep(0.1)  # Avoid tight loop if camera fails
                continue
                
            # Convert to grayscale for AprilTag detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect AprilTags
            tags = self.detector.detect_tags(gray)
            
            # Update statistics
            with self.stats_lock:
                self.stats["tags_detected"] = len(tags)
                if len(tags) > 0:
                    self.stats["last_detection_time"] = datetime.now().strftime("%H:%M:%S")
                
                # Calculate FPS
                self.frame_count += 1
                elapsed_time = time.time() - self.start_time
                if elapsed_time > 1.0:  # Update FPS every second
                    self.stats["processing_fps"] = round(self.frame_count / elapsed_time, 1)
                    self.frame_count = 0
                    self.start_time = time.time()
            
            # Draw tags on the frame
            annotated_frame = self.detector.draw_tags(frame, tags)
            
            # Add FPS text
            cv2.putText(annotated_frame, f"FPS: {self.stats['processing_fps']}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Store the processed frame
            with self.frame_lock:
                _, buffer = cv2.imencode('.jpg', annotated_frame)
                self.current_frame = buffer.tobytes()
                
            # Small delay to control processing rate
            time.sleep(0.01)
            
    def generate_frames(self):
        """
        Generator function that yields frames for streaming
        
        Yields:
            bytes: JPEG encoded frame
        """
        while True:
            # Wait until we have a frame
            while self.current_frame is None and self.processing:
                time.sleep(0.1)
                
            if not self.processing:
                break
                
            # Get current frame
            with self.frame_lock:
                frame_data = self.current_frame
                
            # Yield frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                   
            # Small delay to control streaming rate
            time.sleep(0.05)
            
    def get_stats(self):
        """
        Get current detection statistics as JSON
        
        Returns:
            str: JSON formatted statistics
        """
        with self.stats_lock:
            return json.dumps(self.stats)
