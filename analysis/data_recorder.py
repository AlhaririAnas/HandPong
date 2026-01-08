"""
analysis/data_recorder.py

A standalone tool for recording raw sensor data to evaluate filter performance.
It captures raw vs. smoothed angles and saves them to CSV for analysis.
"""

import os
import cv2
import mediapipe as mp
import time
import math
import csv

from src.core.utils import ExponentialMovingAverage


class DataRecorder:
    """Records hand tracking data for filter performance analysis."""

    def __init__(self):
        """Initialize the data recorder with configuration."""
        # Configuration for the session
        self.output_dir = os.path.join("analysis", "data")
        self.target_angles = []
        self.duration_per_sample = 10
        self.show_skeleton = True

        # Setup MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Use the same filter logic as the game
        self.ema_filter = ExponentialMovingAverage(alpha=0.2)

    def _ensure_directory(self):
        """Creates the data directory if it does not exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created directory: {self.output_dir}")

    def _get_user_config(self):
        """Asks the user for session details via the console."""
        print("\n--- DATA RECORDER SETUP ---")
        try:
            num = int(input("Number of samples (angles) to record? (e.g. 5): "))
            print(f"Enter the {num} target angles:")
            for i in range(num):
                ang = float(input(f" -> Angle for Sample {i+1} (deg): "))
                self.target_angles.append(ang)

            dur = input("Duration per sample in seconds (default 10): ")
            self.duration_per_sample = float(dur) if dur else 10.0

            skel = input("Show Skeleton Overlay? (y/n, default y): ").lower()
            self.show_skeleton = False if skel == "n" else True

            return True
        except ValueError:
            print("Invalid input. Please enter numbers only.")
            return False

    def _calculate_angle_from_landmarks(self, hand_landmarks):
        """
        Calculates the raw angle for the paddle control.
        Uses the same geometry logic as the main game controller.
        """
        # Landmarks: 4=ThumbTip, 5=IndexMCP, 6=IndexPIP
        p4 = hand_landmarks.landmark[4]
        p5 = hand_landmarks.landmark[5]
        p6 = hand_landmarks.landmark[6]

        # Calculate Anchor (midpoint between knuckles 5 and 6)
        anchor_x = (p5.x + p6.x) / 2
        anchor_y = (p5.y + p6.y) / 2

        # Calculate vector from Anchor to Thumb Tip
        dx = p4.x - anchor_x
        dy = -(p4.y - anchor_y)  # Invert Y because screen Y grows downwards

        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        return angle_deg % 360

    def _draw_overlay(self, image, target_angle, idx, state, fps, countdown=0):
        """Draws the UI feedback on the camera feed."""
        h, w, _ = image.shape
        center = (w // 2, h // 2)
        radius = 150

        # Draw FPS
        cv2.putText(
            image,
            f"FPS: {int(fps)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        # Draw Guide Circle
        cv2.circle(image, center, radius, (200, 200, 200), 2)

        # Draw Target Line (Green)
        rad = math.radians(target_angle)
        end_x = int(center[0] + radius * math.cos(rad))
        end_y = int(center[1] - radius * math.sin(rad))
        cv2.line(image, center, (end_x, end_y), (0, 255, 0), 3)

        # Info Text
        info_text = f"SAMPLE {idx + 1} / {len(self.target_angles)}"
        cv2.putText(
            image, info_text, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 100, 0), 2
        )
        cv2.putText(
            image,
            f"TARGET: {target_angle} deg",
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        # State Messages
        if state == "WAIT":
            msg = "ALIGN HAND -> PRESS SPACE"
            cv2.putText(
                image,
                msg,
                (w // 2 - 200, h - 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 255, 255),
                2,
            )
        elif state == "COUNTDOWN":
            cv2.putText(
                image,
                str(countdown),
                (w // 2 - 50, h // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                5.0,
                (0, 0, 255),
                10,
            )
        elif state == "RECORDING":
            cv2.circle(image, (w - 50, 50), 20, (0, 0, 255), -1)

    def run(self):
        """Main loop for the recording session."""
        if not self._get_user_config():
            return

        self._ensure_directory()

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Camera not found.")
            return

        csv_data = []
        global_time = 0.0
        prev_time = 0

        print("\n--- STARTING SESSION ---")
        print("Window opening... Follow instructions on screen.")

        # Iterate through each target angle defined by the user
        for idx, target in enumerate(self.target_angles):
            self.ema_filter.reset()
            state = "WAIT"
            start_time_state = 0

            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break

                # Calculate FPS
                now = time.time()
                fps = 1 / (now - prev_time) if prev_time > 0 else 0
                prev_time = now

                # Input Handling
                key = cv2.waitKey(5) & 0xFF
                if key == 27:  # ESC to quit
                    cap.release()
                    cv2.destroyAllWindows()
                    return

                # Process Frame
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb_frame)

                raw_angle = 0
                filtered_angle = 0

                if results.multi_hand_landmarks:
                    for lms in results.multi_hand_landmarks:
                        if self.show_skeleton:
                            self.mp_draw.draw_landmarks(
                                frame, lms, self.mp_hands.HAND_CONNECTIONS
                            )
                        raw_angle = self._calculate_angle_from_landmarks(lms)
                        filtered_angle = self.ema_filter.update(raw_angle)

                # State Machine
                if state == "WAIT":
                    self._draw_overlay(frame, target, idx, "WAIT", fps)
                    if key == 32:  # SPACE
                        state = "COUNTDOWN"
                        start_time_state = time.time()

                elif state == "COUNTDOWN":
                    elapsed = time.time() - start_time_state
                    count_val = 3 - int(elapsed)
                    self._draw_overlay(frame, target, idx, "COUNTDOWN", fps, count_val)
                    if elapsed > 3:
                        state = "RECORDING"
                        start_time_state = time.time()

                elif state == "RECORDING":
                    rec_elapsed = time.time() - start_time_state
                    self._draw_overlay(frame, target, idx, "RECORDING", fps)

                    # Record data if hand is detected
                    if results.multi_hand_landmarks:
                        timestamp = global_time + rec_elapsed
                        # Columns: timestamp, sample_id, target, raw, filtered
                        csv_data.append(
                            [timestamp, idx + 1, target, raw_angle, filtered_angle]
                        )

                    # Progress bar
                    cv2.putText(
                        frame,
                        f"Rec: {rec_elapsed:.1f} / {self.duration_per_sample}s",
                        (30, 130),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        1,
                    )

                    if rec_elapsed >= self.duration_per_sample:
                        break  # Move to next sample

                cv2.imshow("Data Recorder", frame)

            global_time += self.duration_per_sample

        # Cleanup and Save
        cap.release()
        cv2.destroyAllWindows()
        self._save_to_csv(csv_data)

    def _save_to_csv(self, data):
        """Writes the collected data to a timestamped CSV file."""
        if not data:
            print("No data recorded.")
            return

        filename = "evaluation_data.csv"
        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "timestamp",
                        "sample_id",
                        "target_angle",
                        "raw_angle",
                        "filtered_angle",
                    ]
                )
                writer.writerows(data)
            print(f"\nSuccess! Data saved to: {filepath}")
        except IOError as e:
            print(f"Error saving file: {e}")
