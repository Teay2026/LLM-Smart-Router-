from src.api import app as original_app
from fastapi import FastAPI

# Create a new FastAPI app that mounts the original app under /api
app = FastAPI()

# Add a root endpoint for the main app (serves the API info at /api)
@app.get("/api")
async def api_root():
    return {
        "service": "LLM Smart Router",
        "version": "1.0.0",
        "mode": "mock",
        "message": "🚀 Demo version running in mock mode! This showcases the routing logic with simulated responses.",
        "local_setup": "To run with real models locally: set MOCK_MODE=false and ensure Ollama is running",
        "endpoints": {
            "chat": "/api/route/chat",
            "health": "/api/healthz",
            "metrics": "/api/metrics"
        }
    }

# Mount the original app under /api prefix
app.mount("/api", original_app)

# Export for Vercel
handler = app