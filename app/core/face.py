import numpy as np
import cv2
from insightface.app import FaceAnalysis
from app.core.types import FaceEmbedding, FaceRecognizer
import logging

logger = logging.getLogger(__name__)

class InsightFaceEngine:
    def __init__(self, model_name: str = "buffalo_l"):
        self.app = FaceAnalysis(name=model_name, providers=['CPUExecutionProvider'])
        # Prepare the model with context size (0 means any size, basically init)
        try:
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            logger.info(f"InsightFace model {model_name} loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load InsightFace model: {e}")
            raise

    def get_embedding(self, image_data: bytes | np.ndarray) -> FaceEmbedding:
        if isinstance(image_data, bytes):
            # Decode image
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            img = image_data

        if img is None:
            raise ValueError("Invalid image data")

        faces = self.app.get(img)
        if not faces:
            raise ValueError("No face detected in image")
        
        # Sort by size (largest face) to avoid background faces
        faces = sorted(faces, key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1]), reverse=True)
        target_face = faces[0]
        
        # InsightFace returns float32, need pure python float list for json serialization/db
        embedding = target_face.normed_embedding.tolist()
        return embedding

    def compute_similarity(self, vec1: FaceEmbedding, vec2: FaceEmbedding) -> float:
        # Cosine similarity for normalized vectors is just dot product
        # InsightFace embeddings are already normalized
        return float(np.dot(vec1, vec2))

# Global instance
# face_engine = InsightFaceEngine() # Initialize conditionally to avoid import side effects during tests
