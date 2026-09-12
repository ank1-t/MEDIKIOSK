"""
MediKiosk FastAPI Application Entrypoint
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api.v1.router import router as api_v1_router

# Create database tables automatically upon startup
Base.metadata.create_all(bind=engine)

# Ensure uploads directory exists
uploads_dir = Path("./uploads")
uploads_dir.mkdir(exist_ok=True, parents=True)

app = FastAPI(
    title="MediKiosk API",
    description="AI-Powered Clinical History & Medical Intake Platform",
    version="0.1.0",
)

# Enable CORS for local kiosk and web frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded documents statically so frontend can preview images
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Support both /api and /api/v1 prefixes
app.include_router(api_v1_router, prefix="/api")
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Health check endpoint returning ok status."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
