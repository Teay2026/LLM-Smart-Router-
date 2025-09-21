#!/bin/bash
# LLM Smart Router - Easy Start Script

echo "🚀 Starting LLM Smart Router..."
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install it first:"
    echo "   macOS: brew install ollama"
    echo "   Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "   Windows: Download from https://ollama.ai/download"
    exit 1
fi

# Check if Python dependencies are installed
if ! python -c "import fastapi, uvicorn" &> /dev/null; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Check if Node.js dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd frontend && npm install && cd ..
fi

# Start Ollama if not running
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "🔄 Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Pull model if not available
if ! ollama list | grep "llama3.2:1b" &> /dev/null; then
    echo "📥 Downloading llama3.2:1b model (this may take a few minutes)..."
    ollama pull llama3.2:1b
fi

echo ""
echo "✅ Setup complete! Starting services..."
echo ""

# Start backend
echo "🔧 Starting backend (port 8000)..."
MOCK_MODE=false python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend (port 3000)..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 LLM Smart Router is running!"
echo ""
echo "📍 Frontend: http://localhost:3000"
echo "📍 Backend API: http://localhost:8000"
echo "📍 Health Check: http://localhost:8000/healthz"
echo ""
echo "🧪 Try these test queries:"
echo "   Creative: 'Write a story about robots'"
echo "   Factual: 'What is the capital of France?'"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
wait