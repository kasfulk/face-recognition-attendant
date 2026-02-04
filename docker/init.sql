CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    embedding VECTOR(512) NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);
