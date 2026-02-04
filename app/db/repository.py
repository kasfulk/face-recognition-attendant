from app.db.session import database
from app.db.models import employees, attendance
from app.core.types import FaceEmbedding
from typing import Optional
from sqlalchemy import insert, select, func

# Note: We use cosine distance. Similarity = 1 - distance.
# So if we want similarity >= 0.6, we need distance <= 0.4 (approx, depends on implementation)
# pgvector cosine operator (<=>) returns 1 - cosine_similarity.
# So distance 0 means identical, 1 means orthogonal, 2 means opposite.
# High similarity means LOW distance.
# Threshold 0.6 similarity corresponds to 1 - 0.6 = 0.4 distance.

class EmployeeRepository:
    @staticmethod
    async def create_employee(user_id: str, embedding: FaceEmbedding) -> int:
        query = insert(employees).values(user_id=user_id, embedding=embedding).returning(employees.c.id)
        return await database.execute(query)

    @staticmethod
    async def find_employee_by_id(user_id: str):
        query = select(employees).where(employees.c.user_id == user_id)
        return await database.fetch_one(query)

    @staticmethod
    async def find_nearest_neighbor(embedding: FaceEmbedding, limit: int = 1):
        # Using cosine distance operator
        query = select(
            employees.c.user_id,
            employees.c.embedding.cosine_distance(embedding).label("distance")
        ).order_by(
            employees.c.embedding.cosine_distance(embedding)
        ).limit(limit)
        
        return await database.fetch_all(query)

class AttendanceRepository:
    @staticmethod
    async def log_attendance(user_id: str, confidence: float) -> int:
        query = insert(attendance).values(user_id=user_id, confidence=confidence).returning(attendance.c.id)
        return await database.execute(query)
