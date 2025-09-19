# LLM Smart Router - Technical Overview

The LLM Smart Router is a **FastAPI-based microservice** that analyzes incoming chat requests and intelligently routes them between **LLaMA 3.2 1B models** via Ollama using advanced heuristics.

## Core Features

### 🧠 Intelligent Routing
- **Query Analysis**: Analyzes content and context to determine optimal model
- **Cost Optimization**: Routes to appropriate models based on task complexity
- **Latency Optimization**: Fast model selection for time-sensitive requests

### 📊 Advanced Heuristics
- **Content-Based Routing**:
  - Creative mode: Routes creative tasks to higher temperature model
  - Fast mode: Always routes to optimized fast model
  - Fast requests: LLaMA 3.2 1B Fast for quick factual responses
  - Creative requests: LLaMA 3.2 1B Creative for detailed content generation
  - Default routes to fast model for cost efficiency

### 🚀 Performance Features
- **Latency-First Mode** (`latency_hint=fast`): Always prioritizes fast model
- **Load Balancing**: Monitor queue depths and automatic failover
- **Circuit Breaker**: Automatic fallback when models are overloaded

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Request Flow                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   User   │───▶│   Router    │───▶│       Ollama        │  │
│  │ Request  │    │  Analysis   │    │    LLaMA 3.2 1B     │  │
│  └──────────┘    └─────────────┘    └─────────────────────┘  │
│                         │                       │             │
│                         ▼                       ▼             │
│               ┌─────────────────┐    ┌─────────────────────┐  │
│               │   Model Selection│    │     Response       │  │
│               │   Based on:      │    │    Generation      │  │
│               │   • Content Type │    └─────────────────────┘  │
│               │   • Latency Hint │                             │
│               │   • Queue Depth  │                             │
│               └─────────────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

### Model Configurations

- **🚀 Fast Model**: LLaMA 3.2 1B with low temperature (0.3)
  - Optimized for factual queries, summaries, quick responses
  - Lower temperature for consistent, focused answers
  - Shorter response length (256 tokens)

- **🎨 Creative Model**: LLaMA 3.2 1B with high temperature (0.8)
  - Optimized for creative writing, storytelling, complex reasoning
  - Higher temperature for more diverse, creative responses
  - Longer response length (768 tokens)

## Routing Logic Examples

### ⚡ Fast Factual Tasks → LLaMA 3.2 1B Fast

**Query**: "What is the capital of France?"
**Expected**: 🚀 llama3.2-1b-fast | factual+fast | ~200ms

**Query**: "Define machine learning"
**Expected**: 🚀 llama3.2-1b-fast | factual+fast | ~180ms

**Query**: "How many days in February?"
**Expected**: 🚀 llama3.2-1b-fast | factual+fast | ~150ms

### 🎨 Creative Content → LLaMA 3.2 1B Creative

**Query**: "Write a story about a robot discovering friendship"
**Expected**: 🎨 llama3.2-1b-creative | creative+preferred | ~1200ms

**Query**: "Create a poem about autumn"
**Expected**: 🎨 llama3.2-1b-creative | creative+preferred | ~1000ms

### 📄 Summarization Tasks

**Query**: "Summarize the benefits of renewable energy"
**Expected**: 🚀 llama3.2-1b-fast | summarization+fast | ~250ms

**Query**: "Briefly explain quantum computing" (with fast hint)
**Expected**: 🚀 llama3.2-1b-fast | summarization+fast | ~200ms

### 🔄 Fallback Scenarios

Note: If Creative model is "busy" (queue full), should fallback to Fast model
**Query**: "Write a creative story" (when creative model overloaded)
**Expected**: 🚀 llama3.2-1b-fast | creative+fallback | ~300ms

## Configuration

### Model Endpoints
```yaml
models:
  llama3.2-1b-fast:
    endpoint: "http://localhost:11434/api/chat"
    model_name: "llama3.2:1b"
    cost_per_token: 0.0001
    max_queue_depth: 10
    preferred_for: ["fast", "simple"]

  llama3.2-1b-creative:
    endpoint: "http://localhost:11434/api/chat"
    model_name: "llama3.2:1b"
    cost_per_token: 0.0001
    max_queue_depth: 8
    preferred_for: ["creative", "complex", "reasoning"]

routing:
  fallback_model: "llama3.2-1b-fast"
```

### Deployment Options

```bash
# Full stack with Ollama
docker-compose up -d

# Minimal Ollama-only setup
docker-compose -f docker-compose.ollama-tiny.yml up -d

# Mock mode for testing
docker-compose -f docker-compose.simple.yml up -d
```

## API Response Format

```json
{
  "model_selected": "llama3.2-1b-creative",
  "completion": "Generated response text...",
  "meta": {
    "reason": "creative+preferred",
    "latency_ms": 1250,
    "queue_depth": 0
  }
}
```

### Reason Codes
- `creative+preferred`: Creative query routed to creative model
- `factual+fast`: Factual query with fast latency hint
- `summarization+fast`: Summarization task routed to fast model
- `unknown+fallback`: Unknown query type using fallback
- `creative+fallback`: Creative query fallback due to overload

## Testing Strategy

### Comprehensive Test Suite
The system includes a test harness that validates:

```python
# Test creative routing
test_cases = [
    {
        "query": "Write a haiku about programming",
        "expected_model": "llama3.2-1b-creative",
        "expected_reason": "creative+preferred"
    },
    {
        "query": "What is 2+2?",
        "latency_hint": "fast",
        "expected_model": "llama3.2-1b-fast",
        "expected_reason": "factual+fast"
    }
]
```

### Expected Distribution
- **~60% should route to Fast model** (factual/fast tasks)
- **~40% should route to Creative model** (creative tasks)

## Performance Characteristics

### Latency Expectations
- **Fast Model**: 150-400ms average response time
- **Creative Model**: 800-1500ms average response time
- **Network Overhead**: ~50ms additional latency

### Resource Usage
- **Memory**: ~2-4GB for LLaMA 3.2 1B models
- **CPU**: Moderate usage, scales with concurrent requests
- **Storage**: ~1.3GB per model download

## Monitoring & Observability

### Prometheus Metrics
- **Model Selection Distribution**: Track routing decisions
- **Latency Histograms**: Monitor response times per model
- **Queue Depth Monitoring**: Prevent overload conditions
- **Error Rates**: Track failures and fallbacks

### Grafana Dashboard
- **Real-time routing decisions**
- **Latency percentiles (p50, p95, p99)**
- **Model utilization graphs**
- **Error rate trending**

## Tags

`llm` `routing` `fastapi` `react` `typescript` `ollama` `llama` `ai` `machine-learning` `microservices` `prometheus` `grafana` `docker`