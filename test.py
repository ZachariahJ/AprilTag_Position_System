#!/usr/bin/env python3
"""
AprilTag 6DOF Detection System with Web Interface
Combines Picamera2, AprilTag detection, and Flask frontend
"""
from flask import Flask, render_template, Response, jsonify
import threading
import time
import os
import cv2
import numpy as np
import math
from picamera2 import Picamera2
from pupil_apriltags import Detector

# Create Flask application
app = Flask(__name__, 
            static_folder='frontend/static',
            template_folder='frontend/templates')

class AprilTag6DOFDetector:
    def __init__(self, tag_family="tag36h11", tag_size=0.05):
        """
        Initialize AprilTag detector
        
        Args:
            tag_family: AprilTag family (default: tag36h11)
            tag_size: Tag size in meters (default: 5cm)
        """
        self.tag_family = tag_family
        self.tag_size = tag_size
        
        # Initialize detector with the specified family
        self.detector = Detector(
            families=self.tag_family,
            nthreads=4,
            quad_decimate=1.0,    # Lower for better accuracy, higher for speed
            quad_sigma=0.0,
            refine_edges=1,
            decode_sharpening=0.25,
            debug=0
        )
        
        # Camera intrinsic parameters (should be calibrated for your camera)
        self.intrinsic_matrix = self.get_camera_intrinsics()
        
        # Colors for visualization
        self.tag_color = (0, 165, 255)  # Orange
        self.text_color = (0, 255, 255) # Yellow
        
    def get_camera_intrinsics(self):
        """Get camera intrinsic parameters for OV5647 (Raspberry Pi Camera v1)"""
        # Camera parameters for OV5647 sensor
        # These values are approximate and may need calibration for your specific camera
        fx = 2800.0  # focal length x
        fy = 2800.0  # focal length y
        cx = 1296.0 / 2  # principal point x (half of default width)
        cy = 972.0 / 2   # principal point y (half of default height)
        
        # Camera intrinsic matrix
        camera_matrix = np.array([
            [fx, 0, cx],
            [0, fy, cy],
            [0, 0, 1]
        ])
        
        return camera_matrix
    
    def get_family(self):
        """Return the tag family being detected"""
        return self.tag_family
        
    def detect_tags(self, frame):
        """
        Detect AprilTags in a frame and estimate 6DOF pose
        
        Args:
            frame: RGB image
            
        Returns:
            list: Detected tags with pose information
        """
        if frame is None:
            return []
            
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect tags with pose estimation
            return self.detector.detect(
                gray, 
                estimate_tag_pose=True,
                camera_params=(
                    self.intrinsic_matrix[0, 0],  # fx
                    self.intrinsic_matrix[1, 1],  # fy
                    self.intrinsic_matrix[0, 2],  # cx
                    self.intrinsic_matrix[1, 2]   # cy
                ),
                tag_size=self.tag_size
            )
        except Exception as e:
            print(f"Error detecting AprilTags: {str(e)}")
            return []
    
    def calculate_pose_metrics(self, tag):
        """Calculate 6DOF metrics from tag detection"""
        # Extract rotation and translation matrices
        R = tag.pose_R  # 3x3 rotation matrix
        t = tag.pose_t  # 3x1 translation vector
        
        # Calculate distance (Euclidean norm of translation vector)
        distance = np.linalg.norm(t)
        
        # Convert rotation matrix to Euler angles (in radians)
        # This follows the convention: R = Rz(yaw) * Ry(pitch) * Rx(roll)
        roll = math.atan2(R[2, 1], R[2, 2])
        pitch = math.atan2(-R[2, 0], math.sqrt(R[2, 1]**2 + R[2, 2]**2))
        yaw = math.atan2(R[1, 0], R[0, 0])
        
        # Convert to degrees
        roll_deg = math.degrees(roll)
        pitch_deg = math.degrees(pitch)
        yaw_deg = math.degrees(yaw)
        
        # Calculate direction vector (normalized translation)
        direction = t.flatten() / distance if distance > 0 else np.zeros(3)
        
        return {
            "distance": distance,
            "angles": {
                "roll": roll_deg,
                "pitch": pitch_deg,
                "yaw": yaw_deg
            },
            "direction": direction.tolist(),
            "position": {
                "x": float(t[0][0]),
                "y": float(t[1][0]),
                "z": float(t[2][0])
            }
        }
    
    def draw_tags(self, frame, tags):
        """
        Draw detected AprilTags with 6DOF information
        
        Args:
            frame: Image to draw on
            tags: List of detected tags
            
        Returns:
            Image with annotations
        """
        if frame is None or not tags:
            return frame
            
        annotated_frame = frame.copy()
        
        for tag in tags:
            # Extract tag information
            tag_id = tag.tag_id
            corners = tag.corners.astype(int)
            center = (int(tag.center[0]), int(tag.center[1]))
            
            # Calculate pose metrics
            metrics = self.calculate_pose_metrics(tag)
            
            # Draw tag outline
            cv2.polylines(annotated_frame, [corners.reshape((-1, 1, 2))], True, self.tag_color, 2)
            
            # Draw tag center
            cv2.circle(annotated_frame, center, 5, self.tag_color, -1)
            
            # Draw tag ID and basic info
            basic_info = f"ID: {tag_id} - {metrics['distance']:.2f}m"
            cv2.putText(annotated_frame, basic_info, (center[0] - 20, center[1] - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.tag_color, 2)
            
            # Draw pose information
            pose_info = [
                f"Roll: {metrics['angles']['roll']:.1f}°",
                f"Pitch: {metrics['angles']['pitch']:.1f}°",
                f"Yaw: {metrics['angles']['yaw']:.1f}°",
                f"Dir: {metrics['direction'][0]:.2f}, {metrics['direction'][1]:.2f}, {metrics['direction'][2]:.2f}"
            ]
            
            for i, line in enumerate(pose_info):
                y_pos = center[1] + 20 + (i * 20)
                cv2.putText(annotated_frame, line, (center[0] - 20, y_pos),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.text_color, 1)
                        
        # Add total count
        cv2.putText(annotated_frame, f"Tags detected: {len(tags)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.text_color, 2)
        
        return annotated_frame

class CameraManager:
    def __init__(self, resolution=(640, 640)):
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
            "last_detection_time": None,
            "pose_data": []  # Store pose data for each detected tag
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
        import datetime
        
        while self.processing:
            # Get frame from camera
            frame = self.camera.capture_frame()
            if frame is None:
                time.sleep(0.1)  # Avoid tight loop if camera fails
                continue
                
            # Detect AprilTags with 6DOF pose estimation
            tags = self.detector.detect_tags(frame)
            
            # Process pose data for each tag
            pose_data = []
            for tag in tags:
                metrics = self.detector.calculate_pose_metrics(tag)
                pose_data.append({
                    "tag_id": int(tag.tag_id),
                    "distance": float(metrics["distance"]),
                    "angles": metrics["angles"],
                    "direction": metrics["direction"],
                    "position": metrics["position"]
                })
            
            # Update statistics
            with self.stats_lock:
                self.stats["tags_detected"] = len(tags)
                self.stats["pose_data"] = pose_data
                
                if len(tags) > 0:
                    self.stats["last_detection_time"] = datetime.datetime.now().strftime("%H:%M:%S")
                
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
            dict: Statistics including pose data
        """
        with self.stats_lock:
            return self.stats

# Initialize components
camera = CameraManager(resolution=(800, 600))
detector = AprilTag6DOFDetector(tag_family="tag36h11", tag_size=0.02)  # 5cm tag
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
    return jsonify(processor.get_stats())

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