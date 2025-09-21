from src.api import app

# This is the Vercel handler for the FastAPI app
def handler(request, context):
    return app(request, context)