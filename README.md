# LLM Smart Router

A simple FastAPI service that intelligently routes chat requests between different LLaMA 3.2 models via Ollama based on query type and latency requirements.

## ⚡ Quick Start Guide

**Want to test it right now?** Just run one command:

```bash
./start.sh
```

Or follow these manual steps:

```bash
# 1. Start Ollama with the model
ollama serve
ollama pull llama3.2:1b

# 2. Start the backend (in a new terminal)
MOCK_MODE=false python main.py

# 3. Start the frontend (in another terminal)
cd frontend && npm run dev
```

Then open **http://localhost:3000** and start chatting! 🚀

## Features

- **Intelligent Routing**: Automatically selects optimal models based on content analysis
- **Query Type Detection**: Routes creative vs factual queries to appropriate models
- **Latency Optimization**: Fast model selection for time-sensitive requests
- **Real-time Metrics**: Prometheus integration for monitoring
- **Web Interface**: React frontend for testing and interaction

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │───▶│  FastAPI Router │───▶│     Ollama      │
│  (Frontend)     │    │   (Backend)     │    │  (LLaMA 3.2)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Models

- **LLaMA 3.2 1B Fast**: Optimized for quick factual responses (low temperature)
- **LLaMA 3.2 1B Creative**: Higher temperature for creative tasks

## Quick Start

## 🎯 Testing Guide

### Test Different Query Types

The router intelligently selects models based on your query. Try these examples:

#### 🎨 Creative Queries → **LLaMA 3.2 1B Creative**
```
"Write a story about a robot discovering emotions"
"Create a poem about the ocean"
"Imagine what life would be like on Mars"
"Write a song about coding"
```

#### ⚡ Factual Queries → **LLaMA 3.2 1B Fast**
```
"What is the capital of France?"
"Explain how photosynthesis works"
"What year was the internet invented?"
"Define machine learning"
```

#### 🚀 Fast Mode (Any Query) → **LLaMA 3.2 1B Fast**
Enable "Fast" latency hint in the UI, or add `"latency_hint": "fast"` to API calls.

### Watch the Magic ✨

- **Model Selection**: See which model was chosen and why
- **Response Times**: Compare latency between creative and fast models
- **Routing Reasons**: Understand the decision logic
- **Queue Depth**: Monitor model load in real-time

### Alternative Setup Options

#### 🐳 Docker Setup (All-in-One)

```bash
# Start everything with Docker
docker-compose up -d

# Wait for model download (5-10 minutes first time)
# Access: http://localhost:3000
```

#### 🛠️ Manual Setup (Step by Step)

```bash
# 1. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 2. Start Ollama
ollama serve
ollama pull llama3.2:1b

# 3. Start Backend (real LLMs)
MOCK_MODE=false python main.py

# 4. Start Frontend
cd frontend && npm run dev
```

#### 📊 Mock Mode (No Ollama Required)

```bash
# For demonstration without installing Ollama
python main.py  # MOCK_MODE=true by default
cd frontend && npm run dev
```

## 📡 API Testing

### Web Interface
Visit **http://localhost:3000** and try the examples above!

### Direct API Calls

#### Test Creative Routing
```bash
curl -X POST "http://localhost:8000/route/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Write a haiku about coding"}],
    "latency_hint": "normal"
  }'
```

#### Test Factual Routing
```bash
curl -X POST "http://localhost:8000/route/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is the capital of Japan?"}],
    "latency_hint": "normal"
  }'
```

#### Test Fast Mode Override
```bash
curl -X POST "http://localhost:8000/route/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Write a story"}],
    "latency_hint": "fast"
  }'
```

**Expected Response Format:**
```json
{
  "model_selected": "llama3.2-1b-creative",
  "completion": "Code flows like water...",
  "meta": {
    "reason": "creative+preferred",
    "latency_ms": 1250,
    "queue_depth": 0
  }
}
```

### Health Check
```bash
curl http://localhost:8000/healthz
# Should return: {"status": "healthy", "mode": "live"}
```

## Routing Logic

- **Creative queries** ("write", "story", "poem") → Creative model (higher temperature)
- **Fast requests** (`latency_hint=fast`) → Fast model
- **Factual queries** ("what", "when", "where") → Fast model
- **Fallback**: Fast model if creative model is overloaded

## Configuration

Edit `config.yaml` to customize:

```yaml
models:
  llama3.2-1b-fast:
    endpoint: "http://localhost:11434/api/chat"
    model_name: "llama3.2:1b"
    max_queue_depth: 10

  llama3.2-1b-creative:
    endpoint: "http://localhost:11434/api/chat"
    model_name: "llama3.2:1b"
    max_queue_depth: 8

routing:
  keywords:
    creative: ["story", "creative", "write", "poem"]
    factual: ["what", "when", "where", "who"]
  fallback_model: "llama3.2-1b-fast"
```

## API Endpoints

### POST /route/chat

Route a chat request to the appropriate model.

**Request:**
```json
{
  "messages": [{"role": "user", "content": "Your question here"}],
  "latency_hint": "fast|normal",
  "priority": "low|normal|high"
}
```

**Response:**
```json
{
  "model_selected": "llama3.2-1b-creative",
  "completion": "The AI response...",
  "meta": {
    "reason": "creative+preferred",
    "latency_ms": 432,
    "queue_depth": 1
  }
}
```

### GET /metrics

Prometheus-format metrics including:
- `llm_routing_decisions_total`: Count of routing decisions by model/reason
- `llm_request_duration_seconds`: Request latency histogram
- `llm_queue_depth`: Current queue depth per model
- `llm_errors_total`: Error count by model/type

### GET /healthz

Simple health check endpoint.

## Monitoring

- **Prometheus**: http://localhost:9090 - Metrics collection
- **Grafana**: http://localhost:3001 - Dashboard visualization (admin/admin)

## 🔧 Troubleshooting

### Common Issues

#### Ollama Connection Failed
```bash
# Make sure Ollama is running
ollama serve

# Check if model is downloaded
ollama list
# If llama3.2:1b is missing:
ollama pull llama3.2:1b
```

#### Port Already in Use
```bash
# Backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (port 3000)
lsof -ti:3000 | xargs kill -9
```

#### Dependencies Missing
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
cd frontend && npm install
```

#### Environment Variables
```bash
# For real LLMs (requires Ollama)
export MOCK_MODE=false

# For demo mode (no Ollama needed)
export MOCK_MODE=true
```

### Prerequisites

- **Python 3.8+** and pip
- **Node.js 18+** and npm
- **Ollama** (for real LLM responses)
- **Docker** (optional, for containerized setup)

### Installation
```bash
# Install Ollama (macOS)
brew install ollama

# Install Ollama (Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Install Ollama (Windows)
# Download from https://ollama.ai/download
```

## Development

```bash
# Format code (optional)
black src/
isort src/

# Type checking (optional)
mypy src/
```

## Deployment Variants

- `docker-compose.yml` - Full production setup with monitoring
- `docker-compose.ollama-tiny.yml` - Minimal Ollama-only setup
- `docker-compose.simple.yml` - Mock mode for testing

## Performance

- **Latency**: ~200-800ms per request
- **Throughput**: ~10-50 requests/second (depending on hardware)
- **Memory**: ~2-4GB for LLaMA 3.2 1B models

## Project Structure

```
llm-smart-router/
├── src/
│   ├── api.py          # FastAPI app and endpoints
│   ├── router.py       # Routing logic
│   ├── config.py       # Configuration management
│   └── metrics.py      # Prometheus metrics
├── frontend/           # React web interface
├── grafana/            # Grafana configuration
├── config.yaml         # Main configuration
└── docker-compose.yml  # Full stack deployment
```


## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit pull request

## License

MIT License

## Tags

`llm` `routing` `fastapi` `react` `typescript` `ollama` `llama` `ai` `machine-learning` `microservices` `prometheus` `grafana` `docker`