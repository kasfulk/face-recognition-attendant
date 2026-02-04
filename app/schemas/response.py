from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional

class LivenessChallengeEnum(str, Enum):
    BLINK = "BLINK"
    TURN_LEFT = "TURN_LEFT"
    TURN_RIGHT = "TURN_RIGHT"

# API Schemas
class EnrollResponse(BaseModel):
    status: str
    user_id: str

class LivenessStartResponse(BaseModel):
    session_id: str
    challenge: LivenessChallengeEnum

class LivenessVerifyResponse(BaseModel):
    liveness: bool

class AbsenResponse(BaseModel):
    absen: bool
    user_id: str
    confidence: float

# Internal DTOs might go here if needed
