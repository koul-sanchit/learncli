from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Import routers
from app.routers import chat, terminal

# Load environment variables
load_dotenv()

app = FastAPI(
    title="K8s and Git Learning API",
    description="API for mobile app to learn Kubernetes and Git with AI",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(terminal.router)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "online", "message": "K8s and Git Learning API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)