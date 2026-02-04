from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Annotated
import uuid
from app.core.types import UserId, SessionId
from app.core.face import InsightFaceEngine
from app.core.liveness import MediaPipeLivenessEngine
from app.core.store import SessionStore
from app.db.repository import EmployeeRepository, AttendanceRepository
from app.schemas.response import EnrollResponse, LivenessStartResponse, LivenessVerifyResponse, AbsenResponse, LivenessChallengeEnum
from app.api.dependencies import get_face_engine, get_liveness_engine, get_session_store
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/enroll", response_model=EnrollResponse)
async def enroll_employee(
    user_id: Annotated[str, Form()],
    image: Annotated[UploadFile, File()],
    face_engine: InsightFaceEngine = Depends(get_face_engine)
):
    try:
        content = await image.read()
        embedding = face_engine.get_embedding(content)
        
        # Save to DB
        await EmployeeRepository.create_employee(user_id=user_id, embedding=embedding)
        
        return EnrollResponse(status="enrolled", user_id=user_id)
    except Exception as e:
        logger.error(f"Enrollment failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/liveness/start", response_model=LivenessStartResponse)
async def start_liveness(
    liveness_engine: MediaPipeLivenessEngine = Depends(get_liveness_engine),
    store: SessionStore = Depends(get_session_store)
):
    session_id = SessionId(str(uuid.uuid4()))
    challenge = liveness_engine.generate_challenge()
    
    store.create_session(session_id, challenge)
    
    return LivenessStartResponse(session_id=session_id, challenge=LivenessChallengeEnum(challenge))

@router.post("/liveness/verify", response_model=LivenessVerifyResponse)
async def verify_liveness(
    session_id: Annotated[str, Form()],
    image: Annotated[UploadFile, File()],
    liveness_engine: MediaPipeLivenessEngine = Depends(get_liveness_engine),
    store: SessionStore = Depends(get_session_store)
):
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    try:
        content = await image.read()
        result = liveness_engine.verify_frame(SessionId(session_id), content, session.challenge)
        
        if result.is_live and result.challenge_met:
            store.mark_verified(session_id)
            return LivenessVerifyResponse(liveness=True)
        
        return LivenessVerifyResponse(liveness=False)
        
    except Exception as e:
        logger.error(f"Liveness verification failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/absen", response_model=AbsenResponse)
async def submit_attendance(
    session_id: Annotated[str, Form()],
    image: Annotated[UploadFile, File()],
    store: SessionStore = Depends(get_session_store),
    face_engine: InsightFaceEngine = Depends(get_face_engine)
):
    # 1. Check Liveness Status
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.is_verified:
        raise HTTPException(status_code=400, detail="Liveness not verified")
    
    # 2. Recognize Face
    try:
        content = await image.read()
        embedding = face_engine.get_embedding(content)
        
        # 3. Match against DB
        nearest = await EmployeeRepository.find_nearest_neighbor(embedding)
        
        if not nearest:
            raise HTTPException(status_code=404, detail="No matching employee found")
        
        match = nearest[0] # user_id, distance
        # Convert distance to similarity? 
        # We used cosine_distance. Similarity = 1 - distance.
        # Threshold: Sim >= 0.6 => Dist <= 0.4
        distance = match.distance
        similarity = 1.0 - distance
        
        if similarity < 0.6:
            raise HTTPException(status_code=401, detail="Face not recognized (low confidence)")
        
        user_id = match.user_id
        
        # 4. Log Attendance
        await AttendanceRepository.log_attendance(user_id, confidence=float(similarity))
        
        return AbsenResponse(absen=True, user_id=user_id, confidence=float(similarity))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Attendance failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
