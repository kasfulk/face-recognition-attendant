import cv2
import mediapipe as mp
import numpy as np
import uuid
import random
from app.core.types import LivenessChallenge, LivenessResult, SessionId, LivenessDetector
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class MediaPipeLivenessEngine:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        # Initialize FaceMesh with static image mode=True for single frame processing
        # or False for stream (but here we process frame by frame via API)
        # Using refine_landmarks=True for iris landmarks (good for gaze/blink)
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.challenges_map = {
            "BLINK": self._check_blink,
            "TURN_LEFT": self._check_turn_left,
            "TURN_RIGHT": self._check_turn_right
        }

    def generate_challenge(self) -> LivenessChallenge:
        return random.choice(list(self.challenges_map.keys()))

    def verify_frame(self, session_id: SessionId, frame_data: bytes | np.ndarray, challenge: LivenessChallenge) -> LivenessResult:
        if isinstance(frame_data, bytes):
            nparr = np.frombuffer(frame_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            img = frame_data

        if img is None:
            return LivenessResult(is_live=False, challenge_met=False, error="Invalid image")

        # Convert to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)

        if not results.multi_face_landmarks:
            return LivenessResult(is_live=False, challenge_met=False, error="No face detected")

        face_landmarks = results.multi_face_landmarks[0]
        
        # Verify specific challenge
        verifier = self.challenges_map.get(challenge)
        if verifier:
            met = verifier(face_landmarks)
            return LivenessResult(is_live=True, challenge_met=met)
        
        return LivenessResult(is_live=True, challenge_met=False, error="Unknown challenge")

    def _check_blink(self, landmarks) -> bool:
        # Landmarks for eyes (approximate indices)
        # Left eye: 33, 160, 158, 133, 153, 144
        # Right eye: 362, 385, 387, 263, 373, 380
        # Calculate EAR (Eye Aspect Ratio)
        
        def eye_aspect_ratio(eye_points):
            # Vertical distances
            # (using landmark points directly)
            p2_p6 = np.linalg.norm(np.array([landmarks.landmark[eye_points[1]].x, landmarks.landmark[eye_points[1]].y]) - 
                                   np.array([landmarks.landmark[eye_points[5]].x, landmarks.landmark[eye_points[5]].y]))
            p3_p5 = np.linalg.norm(np.array([landmarks.landmark[eye_points[2]].x, landmarks.landmark[eye_points[2]].y]) - 
                                   np.array([landmarks.landmark[eye_points[4]].x, landmarks.landmark[eye_points[4]].y]))
            # Horizontal
            p1_p4 = np.linalg.norm(np.array([landmarks.landmark[eye_points[0]].x, landmarks.landmark[eye_points[0]].y]) - 
                                   np.array([landmarks.landmark[eye_points[3]].x, landmarks.landmark[eye_points[3]].y]))
            
            return (p2_p6 + p3_p5) / (2.0 * p1_p4)

        LEFT_EYE = [33, 160, 158, 133, 153, 144]
        RIGHT_EYE = [362, 385, 387, 263, 373, 380]

        ear_left = eye_aspect_ratio(LEFT_EYE)
        ear_right = eye_aspect_ratio(RIGHT_EYE)
        avg_ear = (ear_left + ear_right) / 2.0
        
        # Blink threshold typically around 0.2 - 0.25
        return avg_ear < 0.22

    def _check_turn_left(self, landmarks) -> bool:
        # Check yaw.
        # Nose tip: 1
        # Left cheek/ear: 234
        # Right cheek/ear: 454
        nose = landmarks.landmark[1].x
        left_ear = landmarks.landmark[234].x
        right_ear = landmarks.landmark[454].x
        
        dist_l = abs(nose - left_ear)
        dist_r = abs(nose - right_ear)
        
        # Only checks valid face presence, prevent div by zero
        if dist_l + dist_r == 0: return False
        
        ratio = dist_r / (dist_l + 1e-6) # Right side is user's left side on screen if mirrored?
        # If user turns LEFT (their left), their RIGHT cheek becomes more visible to camera (if facing camera)
        # Wait, if I turn my head to the LEFT, my nose moves to the LEFT (screen coordinate decreases) and approaches my LEFT ear in 2D projection.
        # So dist_l (nose to left ear) becomes SMALLER. having ratio > 1 means dist_r > dist_l.
        
        # Simpler logic: Nose x coordinate vs center.
        # Assuming center is 0.5.
        # Turn Left -> Nose x < 0.4 
        return nose < 0.4

    def _check_turn_right(self, landmarks) -> bool:
        nose = landmarks.landmark[1].x
        # Turn Right -> Nose x > 0.6
        return nose > 0.6
