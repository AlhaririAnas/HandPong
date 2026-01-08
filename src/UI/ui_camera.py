
import cv2
from config import (
    CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_X, CAMERA_Y,
    CAMERA_BORDER_COLOR, CAMERA_BORDER_WIDTH
)


class CameraPreview:
    """Verwaltet Camera Preview Rendering."""
    
    @staticmethod
    def create_preview(frame, hand_tracker, tracking_result):
        """Erstelle Camera Preview mit Hand Overlay."""
        preview = cv2.resize(frame, (CAMERA_WIDTH, CAMERA_HEIGHT))
        
        if tracking_result['detected']:
            preview = hand_tracker.draw_hand_overlay(
                preview, 
                tracking_result['detected']
            )
        
        return preview
    
    @staticmethod
    def add_to_display(display_frame, camera_preview):
        y1 = CAMERA_Y
        y2 = y1 + CAMERA_HEIGHT
        x1 = CAMERA_X
        x2 = x1 + CAMERA_WIDTH
        
        # Ensure bounds
        if x2 > display_frame.shape[1]:
            x2 = display_frame.shape[1]
            x1 = x2 - CAMERA_WIDTH
        
        if y2 > display_frame.shape[0]:
            y2 = display_frame.shape[0]
            y1 = y2 - CAMERA_HEIGHT
        
        # Blit camera preview
        display_frame[y1:y2, x1:x2] = camera_preview[0:y2-y1, 0:x2-x1]
        
        # Draw border
        cv2.rectangle(
            display_frame, 
            (x1, y1), 
            (x2, y2), 
            CAMERA_BORDER_COLOR, 
            CAMERA_BORDER_WIDTH
        )
        
        return display_frame
