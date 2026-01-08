"""
hand_tracker.py - Pong Game v5.0
Hand-Tracking and Gesture Recognition using MediaPipe
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Tuple, List
from .utils import ExponentialMovingAverage, calculate_angle
from config import MAX_HANDS

class HandTracker:
    """Hand Tracking for paddle control and Menu Gestures."""
    
    HAND_CONNECTIONS = mp.solutions.hands.HAND_CONNECTIONS
    FINGERTIPS = [4, 8, 12, 16, 20] # Thumb, Index, Middle, Ring, Pinky
    
    def __init__(
        self,
        use_right_hand: bool = True,
        smoothing_alpha: float = 0.12,
        confidence_threshold: float = 0.5,
    ):
        self.mp_hands = mp.solutions.hands
        # Increased max_num_hands to 2 to support the "Stop Game" gesture
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_HANDS,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )
        
        self.use_right_hand = use_right_hand
        self.ema_filter = ExponentialMovingAverage(alpha=smoothing_alpha)
        self.last_angle = 180.0
        self.current_landmarks_list = []
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """Process Frame, detect hands, calculate angle and identify gestures."""
        results = self.hands.process(frame)
        
        output = {
            'angle': self.last_angle,
            'detected': False,
            'landmarks_list': [],
            'gesture': None,
            'hands_count': 0
        }
        
        if results.multi_hand_landmarks:
            output['detected'] = True
            output['landmarks_list'] = results.multi_hand_landmarks
            output['hands_count'] = len(results.multi_hand_landmarks)
            
            # 1. Check for STOP Gesture (Two hands, open palms)
            if output['hands_count'] == 2:
                if self._check_stop_gesture(results.multi_hand_landmarks):
                    output['gesture'] = "STOP"
            
            # 2. Process primary hand for Paddle/Menu Control
            # We prioritize the hand matching the configuration (Left vs Right)
            primary_hand_landmarks = None
            
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = handedness.classification[0].label
                # Logic: If use_right_hand is True, we look for "Right".
                if (self.use_right_hand and label == "Right") or \
                   (not self.use_right_hand and label == "Left"):
                    primary_hand_landmarks = hand_landmarks
                    break
            
            # Fallback: if preferred hand not found, use the first one
            if primary_hand_landmarks is None:
                primary_hand_landmarks = results.multi_hand_landmarks[0]

            # Calculate Angle (For Paddle)
            landmarks = primary_hand_landmarks.landmark
            wrist = landmarks[0]
            thumb_tip = landmarks[4]
            angle = calculate_angle((wrist.x, wrist.y), (thumb_tip.x, thumb_tip.y))
            
            smoothed_angle = self.ema_filter.update(angle)
            self.last_angle = smoothed_angle
            output['angle'] = smoothed_angle
            
            # Calculate Gesture (For Menu)
            if output['gesture'] != "STOP":
                output['gesture'] = self._detect_hand_gesture(primary_hand_landmarks)

        self.current_landmarks_list = output['landmarks_list']
        return output

    def _check_stop_gesture(self, landmarks_list) -> bool:
        """Check if both hands are open (5 fingers up)."""
        hands_open = 0
        for hand_landmarks in landmarks_list:
            if self._count_fingers(hand_landmarks) == 5:
                hands_open += 1
        return hands_open == 2

    def _detect_hand_gesture(self, landmarks) -> str:
        """Identify specific gestures: Numbers 1-5, Thumbs Up/Down."""
        fingers_up = self._count_fingers(landmarks)
        
        # Check Thumbs Up/Down specifically
        # (Assumes hand is roughly vertical)
        wrist_y = landmarks.landmark[0].y
        thumb_tip_y = landmarks.landmark[4].y
        index_tip_y = landmarks.landmark[8].y
        
        # Thumbs UP: Thumb is high, others curled (approx 0 fingers or just thumb)
        # Note: _count_fingers might return 0 or 1 for fist/thumb
        is_fist_shape = fingers_up <= 1 
        
        if is_fist_shape:
            # Thumb significantly above wrist (y is inverted in screen coords, so smaller is higher)
            if thumb_tip_y < wrist_y - 0.1: 
                return "THUMBS_UP"
            # Thumb significantly below wrist
            if thumb_tip_y > wrist_y + 0.1:
                return "THUMBS_DOWN"

        # Return number based on finger count
        if fingers_up > 0:
            return str(fingers_up) # "1", "2", "3", "4", "5"
        
        return "NONE"

    def _count_fingers(self, hand_landmarks) -> int:
        """Count how many fingers are extended."""
        landmarks = hand_landmarks.landmark
        count = 0
        
        # Tips ids: [4, 8, 12, 16, 20]
        # PIP ids (knuckles): [2, 6, 10, 14, 18]
        
        # 1. Thumb (Tip x vs IP x) - Logic depends on hand side, simplified here:
        # We check if thumb tip is "far" from the palm center compared to the knuckle
        # Simplified: Check if tip is higher than base for general "open"
        # But specifically for numbers, usually we assume Index/Middle etc.
        # Let's use a Y-check for fingers 2-5
        
        # Fingers: Index(8), Middle(12), Ring(16), Pinky(20)
        # Check if TIP is HIGHER (lower Y value) than PIP joint
        if landmarks[8].y < landmarks[6].y: count += 1  # Index
        if landmarks[12].y < landmarks[10].y: count += 1 # Middle
        if landmarks[16].y < landmarks[14].y: count += 1 # Ring
        if landmarks[20].y < landmarks[18].y: count += 1 # Pinky
        
        # Thumb: Often tricky. Let's say if Thumb Tip is "outside" the Index MCP
        # For simplicity in Menu, let's just count the 4 fingers + 1 if thumb is extended
        # Simple heuristic: Thumb tip distance to Pinky base
        if abs(landmarks[4].x - landmarks[17].x) > 0.15: # Wide spread
             count += 1
             
        return count

    def draw_hand_overlay(self, frame: np.ndarray, detected: bool) -> np.ndarray:
        """Draw hand skeletons on frame."""
        h, w, _ = frame.shape
        
        if detected and self.current_landmarks_list:
            for landmarks in self.current_landmarks_list:
                # Draw Connections
                for connection in self.HAND_CONNECTIONS:
                    start_idx, end_idx = connection
                    start = landmarks.landmark[start_idx]
                    end = landmarks.landmark[end_idx]
                    cv2.line(frame, 
                            (int(start.x * w), int(start.y * h)), 
                            (int(end.x * w), int(end.y * h)), 
                            (0, 200, 255), 2)
                
                # Draw Keypoints
                for i, landmark in enumerate(landmarks.landmark):
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    color = (0, 255, 200) if i == 0 else (255, 0, 200) if i in self.FINGERTIPS else (0, 150, 255)
                    radius = 6 if i == 0 else 5 if i in self.FINGERTIPS else 3
                    cv2.circle(frame, (x, y), radius, color, -1)
        
        return frame
    
    def reset(self):
        self.ema_filter.reset()
        self.last_angle = 180.0
        self.current_landmarks_list = []