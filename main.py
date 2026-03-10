# main.py
from fastapi import FastAPI
from api.endpoints import router as api_router
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Twitter CLI API",
    description="A simple API wrapper for twitter-cli",
    version="0.1.0"
)

# Allow frontend apps to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our API routes with prefix
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "Welcome to Twitter CLI API 🐦",
        "docs": "/docs",
        "health": "/api/v1/health",
        "example": "/api/v1/feed?max_tweets=3"
    }

# Update the uvicorn run section (or create a run.py):
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)