# LLM Smart Router - TypeScript Frontend

A simple, clean React TypeScript interface for testing the LLM Smart Router.

## Features

✨ **Simple Chat Interface**
- Clean, modern UI with gradient background
- Real-time routing visualization
- Interactive controls for latency hints and priority

🎯 **Smart Routing Visualization**
- Color-coded model badges (Creative vs Fast)
- Routing reason indicators (creative, fast, factual, etc.)
- Latency and queue depth metrics
- Real-time health monitoring

🔧 **TypeScript Support**
- Full type safety with API interfaces
- Modern React with hooks
- Vite for fast development

## Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

### 3. Make Sure Backend is Running
The frontend expects the LLM Router API to be running on port 8000:
```bash
cd ..
python main.py
```

## Usage

1. **Open the app** at http://localhost:3000
2. **Check status** - Green "✅ Router Online" means the backend is connected
3. **Enter a message** in the textarea
4. **Set routing options**:
   - **Latency Hint**: `fast` prioritizes LLaMA 3.2 1B Fast, `normal` allows optimal routing
   - **Priority**: `low/normal/high` (currently for demonstration)
5. **Click "Send Message"** to see the routing in action

### Example Queries to Try

**Creative (→ LLaMA 3.2 1B Creative):**
- "Write a creative story about a robot"
- "Compose a poem about nature"
- "Create an imaginative dialogue"

**Fast + Factual (→ LLaMA 3.2 1B Fast):**
- "What is the capital of France?" (with `latency_hint=fast`)
- "Who invented the telephone?"
- "When was the Declaration of Independence signed?"

**Summarization:**
- "Summarize machine learning"
- "Give me a TLDR on artificial intelligence"
- "Briefly explain quantum computing"

## API Integration

The app uses Axios with TypeScript interfaces:

```typescript
interface ChatRequest {
  messages: Message[];
  latency_hint?: 'fast' | 'normal';
  priority?: 'low' | 'normal' | 'high';
}

interface ChatResponse {
  model_selected: string;
  completion: string;
  meta: {
    reason: string;
    latency_ms: number;
    queue_depth: number;
  };
}
```

## Development

### Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run type-check` - Run TypeScript checks

### Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx    # Main chat component
│   │   └── ChatInterface.css    # Styles
│   ├── services/
│   │   └── api.ts              # API client
│   ├── types/
│   │   └── api.ts              # TypeScript interfaces
│   ├── App.tsx                 # Main app with health check
│   ├── App.css                 # Global styles
│   └── main.tsx               # React entry point
├── package.json
├── tsconfig.json
├── vite.config.ts             # Vite config with proxy
└── index.html
```

### Proxy Configuration

The Vite development server proxies API requests:
- Frontend: `http://localhost:3000`
- API calls: `http://localhost:3000/api/*` → `http://localhost:8000/*`

This avoids CORS issues during development.

## Deployment

For production deployment:

1. **Build the frontend:**
   ```bash
   npm run build
   ```

2. **Serve static files** from `dist/` directory

3. **Update API URL** in production to point to your deployed backend

## UI Features

- **Responsive design** - Works on desktop and mobile
- **Real-time health monitoring** - Shows connection status
- **Color-coded routing results** - Easy to understand routing decisions
- **Progressive enhancement** - Works even if some features fail
- **Accessibility** - Proper labels and semantic HTML

The interface is designed to be intuitive for testing and demonstrating the LLM Smart Router's capabilities!