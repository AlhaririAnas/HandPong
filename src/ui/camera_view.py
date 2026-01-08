"""
src/ui/camera_view.py

Renders the Picture-in-Picture (PIP) camera feed with status overlays.
Displays hand tracking debug visualization and current pose/angle information.
"""

import pygame
import cv2
import numpy as np

from config import (
    CAMERA_X,
    CAMERA_Y,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    COLOR_TRACKING_GOOD,
    COLOR_TRACKING_BAD,
    COLOR_UI_TEXT,
)


def draw_camera_pip(surface, frame_bgr, hand_controller):
    """
    Draw the camera PIP overlay with hand tracking debug information.

    Args:
        surface: Pygame surface to draw on
        frame_bgr: OpenCV frame (BGR format)
        hand_controller: HandController instance with current tracking state
    """
    if frame_bgr is None:
        return

    # Draw Debug Skeleton
    frame_debug = hand_controller.draw_debug(frame_bgr.copy())

    # Convert to Pygame Surface
    thumb = cv2.resize(frame_debug, (CAMERA_WIDTH, CAMERA_HEIGHT))
    thumb = cv2.cvtColor(thumb, cv2.COLOR_BGR2RGB)
    thumb = np.transpose(thumb, (1, 0, 2))  # Rotate correctly
    cam_surf = pygame.surfarray.make_surface(thumb)

    # Draw PIP Frame
    active = hand_controller.hands_detected
    status_col = COLOR_TRACKING_GOOD if active else COLOR_TRACKING_BAD

    surface.blit(cam_surf, (CAMERA_X, CAMERA_Y))
    pygame.draw.rect(
        surface, status_col, (CAMERA_X, CAMERA_Y, CAMERA_WIDTH, CAMERA_HEIGHT), 4
    )

    # --- UI OVERLAY ---
    font = pygame.font.SysFont("arial", 24, bold=True)

    # Position Calculations
    # Stack text from bottom up: POSE -> ANGLE
    base_x = CAMERA_X + 10
    bottom_y = CAMERA_Y + CAMERA_HEIGHT - 10

    # Draw POSE (Bottom)
    gesture_name = hand_controller.current_gesture.upper()
    pose_txt = font.render(f"POSE: {gesture_name}", True, COLOR_UI_TEXT)
    pose_rect = pose_txt.get_rect(bottomleft=(base_x, bottom_y))

    # Background for text readability
    bg_rect_pose = pose_rect.inflate(10, 6)
    bg_rect_pose.bottomleft = (base_x, bottom_y + 3)

    s = pygame.Surface((bg_rect_pose.width, bg_rect_pose.height))
    s.set_alpha(180)
    s.fill((0, 0, 0))
    surface.blit(s, bg_rect_pose)
    surface.blit(pose_txt, pose_rect)

    # Draw ANGLE (Above Pose)
    # Only show angle if tracking is active
    if active:
        angle_val = int(hand_controller.current_angle)
        angle_txt = font.render(f"ANGLE: {angle_val}°", True, COLOR_UI_TEXT)
        angle_rect = angle_txt.get_rect(bottomleft=(base_x, pose_rect.top - 5))

        # Background for Angle
        bg_rect_angle = angle_rect.inflate(10, 6)
        bg_rect_angle.bottomleft = (base_x, angle_rect.bottom + 3)

        s2 = pygame.Surface((bg_rect_angle.width, bg_rect_angle.height))
        s2.set_alpha(180)
        s2.fill((0, 0, 0))
        surface.blit(s2, bg_rect_angle)
        surface.blit(angle_txt, angle_rect)
