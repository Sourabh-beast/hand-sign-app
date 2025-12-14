import cv2
import mediapipe as mp
import numpy as np

class HandDetector:
    """
    Hand detection and landmark extraction using MediaPipe.
    Detects up to 2 hands in camera frames and extracts 21 3D landmarks per hand.
    """
    
    def __init__(self, max_hands=2, detection_confidence=0.7, tracking_confidence=0.7):
        """
        Initialize the hand detector.
        
        Args:
            max_hands: Maximum number of hands to detect (default: 2)
            detection_confidence: Minimum detection confidence threshold
            tracking_confidence: Minimum tracking confidence threshold
        """
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        
    def find_hands(self, frame, draw=True):
        """
        Detect hands in frame and optionally draw landmarks.
        
        Args:
            frame: BGR image from camera
            draw: Whether to draw landmarks on frame
            
        Returns:
            frame: Frame with landmarks drawn (if draw=True)
            results: MediaPipe hand detection results
        """
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks and draw:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw connections
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        
        return frame, results
    
    def get_landmarks(self, results, frame_shape):
        """
        Extract normalized landmarks from detection results for the first hand.
        
        Args:
            results: MediaPipe hand detection results
            frame_shape: Shape of the frame (height, width, channels)
            
        Returns:
            landmarks: List of (x, y, z) tuples for 21 landmarks, or None if no hand
        """
        if not results.multi_hand_landmarks:
            return None
        
        # Get first hand's landmarks
        hand_landmarks = results.multi_hand_landmarks[0]
        h, w, _ = frame_shape
        
        landmarks = []
        for lm in hand_landmarks.landmark:
            # Convert to pixel coordinates
            x = lm.x * w
            y = lm.y * h
            z = lm.z  # Keep z as relative depth
            landmarks.append((x, y, z))
        
        return landmarks
    
    def get_all_hands_landmarks(self, results, frame_shape):
        """
        Extract landmarks for all detected hands.
        
        Args:
            results: MediaPipe hand detection results
            frame_shape: Shape of the frame (height, width, channels)
            
        Returns:
            list: List of landmark lists for each hand, or empty list if no hands
        """
        if not results.multi_hand_landmarks:
            return []
        
        h, w, _ = frame_shape
        all_hands = []
        
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = []
            for lm in hand_landmarks.landmark:
                x = lm.x * w
                y = lm.y * h
                z = lm.z
                landmarks.append((x, y, z))
            all_hands.append(landmarks)
        
        return all_hands
    
    def get_hand_count(self, results):
        """Get the number of detected hands."""
        if not results.multi_hand_landmarks:
            return 0
        return len(results.multi_hand_landmarks)
    
    def get_normalized_landmarks(self, results):
        """
        Get landmarks normalized relative to hand bounding box.
        This is useful for gesture classification as it's position-invariant.
        
        Args:
            results: MediaPipe hand detection results
            
        Returns:
            normalized: Flattened array of normalized landmarks, or None
        """
        if not results.multi_hand_landmarks:
            return None
        
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # Extract all landmark coordinates
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.append([lm.x, lm.y, lm.z])
        
        landmarks = np.array(landmarks)
        
        # Normalize relative to wrist (landmark 0)
        wrist = landmarks[0]
        landmarks = landmarks - wrist
        
        # Scale by hand size (distance from wrist to middle finger MCP)
        middle_mcp = landmarks[9]
        scale = np.linalg.norm(middle_mcp)
        if scale > 0:
            landmarks = landmarks / scale
        
        # Flatten to 1D array
        return landmarks.flatten()
    
    def release(self):
        """Release resources."""
        self.hands.close()
