#!/usr/bin/env python3
"""
AprilTag Detector
Handles AprilTag detection using the pupil_apriltags library
"""
import cv2
from pupil_apriltags import Detector

class AprilTagDetector:
    def __init__(self):
        """
        Initialize the AprilTag detector with only the most common family: tag36h11
        """

        self.tag_family = 'tag36h11'

        # Initialize detector with single family
        # Fixed issue: families must be a list, not a string
        self.detector = Detector(
            families=self.tag_family,  # List with single family
            nthreads=1,           # Number of threads to use
            quad_decimate=1.0,    # Image decimation factor
            quad_sigma=0.0,       # Gaussian blur sigma
            refine_edges=1,       # Refine edge features
            decode_sharpening=0.25, # Decode sharpening factor
            debug=0               # Debug flag
        )
        
        # Color for tag visualization (Orange)
        self.tag_color = (0, 165, 255)
        
    def get_family(self):
        """Return the tag family being detected"""
        return self.tag_family
        
    def detect_tags(self, gray_image):
        """
        Detect AprilTags in a grayscale image
        
        Args:
            gray_image (numpy.ndarray): Grayscale image for detection
            
        Returns:
            list: Detected tags
        """
        if gray_image is None:
            return []
            
        try:
            # Detect tags without pose estimation to improve performance
            return self.detector.detect(gray_image, estimate_tag_pose=False)
        except Exception as e:
            print(f"Error detecting AprilTags: {str(e)}")
            return []
            
    def draw_tags(self, frame, tags):
        """
        Draw detected AprilTags on the image
        
        Args:
            frame (numpy.ndarray): Image to draw on
            tags (list): List of detected tags
            
        Returns:
            numpy.ndarray: Annotated image
        """
        if frame is None or not tags:
            return frame
            
        annotated_frame = frame.copy()
        
        for tag in tags:
            # Extract tag information
            tag_id = tag.tag_id
            corners = tag.corners.astype(int)
            center = (int(tag.center[0]), int(tag.center[1]))
            
            # Draw tag outline
            cv2.polylines(annotated_frame, [corners.reshape((-1, 1, 2))], True, self.tag_color, 2)
            
            # Draw tag ID
            label = f"ID: {tag_id}"
            
            # Set text position below the tag
            text_x = center[0] - 20
            text_y = center[1] + 30
            
            # Add background for better text visibility
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(annotated_frame, 
                         (text_x - 5, text_y - text_size[1] - 5), 
                         (text_x + text_size[0] + 5, text_y + 5), 
                         (0, 0, 0), -1)
            
            # Draw text
            cv2.putText(annotated_frame, label, (text_x, text_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.tag_color, 2)
                        
        # Add total count
        cv2.putText(annotated_frame, f"Tags detected: {len(tags)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        return annotated_frame
