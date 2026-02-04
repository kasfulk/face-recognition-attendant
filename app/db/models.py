import sqlalchemy
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Float, DateTime, MetaData, Table, func

metadata = MetaData()

employees = Table(
    "employees",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", String, unique=True, nullable=False),
    Column("embedding", Vector(512), nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

attendance = Table(
    "attendance",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", String, nullable=False),
    Column("confidence", Float, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)
