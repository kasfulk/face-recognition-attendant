from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.db.session import connect_to_db, close_db_connection
from app.api.routes import router
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_db()
    yield
    # Shutdown
    await close_db_connection()

app = FastAPI(
    title="Face-Absen",
    lifespan=lifespan
)

# CORS (Allow all for MVP/local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files (for frontend)
app.mount("/static", StaticFiles(directory="app/templates"), name="static")

# Include API Router
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Face-Absen System Ready", "docs": "/docs"}
