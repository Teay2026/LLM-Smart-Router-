import json
import logging
import uuid
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from .config import Config
from .router import LLMRouter
from .metrics import MetricsCollector


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    latency_hint: Optional[str] = "normal"
    priority: Optional[str] = "normal"


class ChatResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    model_selected: str
    completion: str
    meta: Dict


app = FastAPI(title="LLM Smart Router", version="1.0.0")

config = Config()
router = LLMRouter(config)
metrics = MetricsCollector()


@app.post("/route/chat", response_model=ChatResponse)
async def route_chat(request: ChatRequest):
    request_id = str(uuid.uuid4())

    logger.info(json.dumps({
        "request_id": request_id,
        "latency_hint": request.latency_hint,
        "priority": request.priority,
        "messages_count": len(request.messages)
    }))

    try:
        messages_dict = [msg.dict() for msg in request.messages]
        result = await router.route_request(
            messages=messages_dict,
            latency_hint=request.latency_hint,
            priority=request.priority
        )

        metrics.record_routing_decision(
            result["model_selected"],
            result["meta"]["reason"]
        )

        metrics.record_request_latency(
            result["model_selected"],
            result["meta"]["latency_ms"] / 1000.0
        )

        metrics.update_queue_depth(
            result["model_selected"],
            result["meta"]["queue_depth"]
        )

        logger.info(json.dumps({
            "request_id": request_id,
            "model_selected": result["model_selected"],
            "reason": result["meta"]["reason"],
            "latency_ms": result["meta"]["latency_ms"]
        }))

        return ChatResponse(**result)

    except Exception as e:
        logger.error(json.dumps({
            "request_id": request_id,
            "error": str(e)
        }))
        metrics.record_error("unknown", "request_failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    return Response(
        content=metrics.get_metrics(),
        media_type="text/plain"
    )


@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "mode": "mock" if config.is_mock_mode else "live",
        "note": "This is a demo version running in mock mode. For real LLM responses, run locally with Ollama." if config.is_mock_mode else "Running with real LLM models"
    }

@app.get("/")
async def root():
    return {
        "service": "LLM Smart Router",
        "version": "1.0.0",
        "mode": "mock" if config.is_mock_mode else "live",
        "message": "🚀 Demo version running in mock mode! This showcases the routing logic with simulated responses." if config.is_mock_mode else "Live version with real LLM models",
        "local_setup": "To run with real models locally: set MOCK_MODE=false and ensure Ollama is running" if config.is_mock_mode else None,
        "endpoints": {
            "chat": "/route/chat",
            "health": "/healthz",
            "metrics": "/metrics"
        }
    }