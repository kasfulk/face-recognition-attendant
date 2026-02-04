from typing import NewType, Literal, Protocol, TypedDict, runtime_checkable
from dataclasses import dataclass
from datetime import datetime

# Domain Primitives
UserId = NewType("UserId", str)
FaceEmbedding = list[float]  # 512-dim vector

# Liveness Types
LivenessChallenge = Literal["BLINK", "TURN_LEFT", "TURN_RIGHT"]
SessionId = NewType("SessionId", str)

@dataclass(frozen=True)
class FaceVerificationResult:
    is_match: bool
    confidence: float
    user_id: UserId | None = None

@dataclass(frozen=True)
class LivenessResult:
    is_live: bool
    challenge_met: bool
    error: str | None = None

# Protocols
@runtime_checkable
class FaceRecognizer(Protocol):
    def get_embedding(self, image_data: bytes) -> FaceEmbedding: ...
    def compute_similarity(self, vec1: FaceEmbedding, vec2: FaceEmbedding) -> float: ...

@runtime_checkable
class LivenessDetector(Protocol):
    def generate_challenge(self) -> LivenessChallenge: ...
    def verify_frame(self, session_id: SessionId, frame_data: bytes, challenge: LivenessChallenge) -> LivenessResult: ...
