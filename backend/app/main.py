"""
MediKiosk FastAPI Application Entrypoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

from app.api.v1.router import router as api_v1_router

app.include_router(api_v1_router)

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for platform monitoring."""
    return {
        "status": "healthy",
        "service": "medikiosk-backend",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
