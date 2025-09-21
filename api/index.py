from src.api import app

# Export the FastAPI app for Vercel
# Vercel will automatically handle ASGI mounting
handler = app