from app.core.face import InsightFaceEngine
from app.core.liveness import MediaPipeLivenessEngine
from app.core.store import session_store
import logging

logger = logging.getLogger(__name__)

# Lazy singleton instances
_face_engine = None
_liveness_engine = None

def get_face_engine() -> InsightFaceEngine:
    global _face_engine
    if _face_engine is None:
        logger.info("Initializing Face Engine...")
        _face_engine = InsightFaceEngine()
    return _face_engine

def get_liveness_engine() -> MediaPipeLivenessEngine:
    global _liveness_engine
    if _liveness_engine is None:
        logger.info("Initializing Liveness Engine...")
        _liveness_engine = MediaPipeLivenessEngine()
    return _liveness_engine

def get_session_store():
    return session_store
