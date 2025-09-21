# LLM Smart Router

A simple FastAPI service that intelligently routes chat requests between different LLaMA 3.2 models via Ollama based on query type and latency requirements.

## 🚀 Live Demo

**Try it now**: [https://your-app.vercel.app](https://your-app.vercel.app) (Mock Mode)

> **Note**: The live demo uses simulated responses to showcase the routing logic. For real LLM responses, run locally with Ollama.

### Test the Demo
- Try **creative queries**: "Write a story about a robot" → Routes to Creative model
- Try **factual queries**: "What is the capital of France?" → Routes to Fast model
- Enable **"Fast" latency hint** → Always routes to Fast model
- Watch the **routing decisions** and **response times** in the UI

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

### 🌐 Option 1: Test Online (Mock Mode)
Visit the [live demo](https://your-app.railway.app) to test the routing logic with simulated responses.

### 🖥️ Option 2: Run Locally with Real LLMs

#### Prerequisites
- Docker and Docker Compose
- Or: Python 3.8+, Node.js 18+, and Ollama

#### Docker Setup (Recommended)

```bash
# Start all services
docker-compose up -d

# The router will automatically pull llama3.2:1b model
# Wait for initial model download (can take 5-10 minutes)

# Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Metrics: http://localhost:9090
# Grafana: http://localhost:3001
```

#### Manual Setup

```bash
# 1. Start Ollama
ollama serve
ollama pull llama3.2:1b

# 2. Start Backend (disable mock mode)
export MOCK_MODE=false  # Enable real LLMs
pip install -r requirements.txt
python main.py

# 3. Start Frontend
cd frontend
npm install
npm run dev
```

> **Important**: Set `MOCK_MODE=false` to use real Ollama models instead of mock responses.

## Usage

### Web Interface
Visit http://localhost:3000 to test the router with different query types.

### API Example

```bash
curl -X POST "http://localhost:8000/route/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Write a haiku about coding"}],
    "latency_hint": "normal"
  }'
```

**Response:**
```json
{
  "model_selected": "llama3.2-1b-creative",
  "completion": "Code flows like water\nLogic dancing with pixels\nBugs become features",
  "meta": {
    "reason": "creative+preferred",
    "latency_ms": 1250,
    "queue_depth": 0
  }
}
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

## 🚀 Hosted Demo

**Try it live**: Deploy on [Vercel](https://vercel.com) (free hosting)

The hosted demo runs in **mock mode** with simulated responses to showcase the routing logic. For real LLM responses, run locally with Ollama.

### Deploy to Vercel

1. Fork this repository
2. Go to [vercel.com](https://vercel.com) and sign up
3. Click "New Project" → "Import" from GitHub
4. Select your forked repository
5. Vercel will auto-deploy using the included `vercel.json` configuration

The app will be available at `https://your-app-name.vercel.app`

**Note**: The hosted version uses mock responses. Set `MOCK_MODE=false` locally for real LLM responses.

### Alternative: Deploy to Railway

You can also deploy to Railway:

1. Fork this repository
2. Go to [railway.app](https://railway.app) and sign up
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your forked repository
5. Railway will auto-deploy using the included configuration

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit pull request

## License

MIT License

## Tags

`llm` `routing` `fastapi` `react` `typescript` `ollama` `llama` `ai` `machine-learning` `microservices` `prometheus` `grafana` `docker`