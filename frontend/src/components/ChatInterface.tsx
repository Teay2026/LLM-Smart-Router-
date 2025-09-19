import { useState } from 'react';
import { ChatRequest, ChatResponse, LatencyHint, Priority } from '../types/api';
import { llmRouterApi } from '../services/api';
import './ChatInterface.css';

const ChatInterface = () => {
  const [message, setMessage] = useState('');
  const [latencyHint, setLatencyHint] = useState<LatencyHint>('normal');
  const [priority, setPriority] = useState<Priority>('normal');
  const [responses, setResponses] = useState<ChatResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!message.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const request: ChatRequest = {
        messages: [{ role: 'user', content: message }],
        latency_hint: latencyHint,
        priority: priority,
      };

      const response = await llmRouterApi.routeChat(request);
      setResponses(prev => [response, ...prev]);
      setMessage('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getModelBadgeClass = (model: string) => {
    return model.includes('creative') ? 'model-badge llama-creative' : 'model-badge llama-fast';
  };

  const getReasonBadgeClass = (reason: string) => {
    if (reason.includes('creative')) return 'reason-badge creative';
    if (reason.includes('fast')) return 'reason-badge fast';
    if (reason.includes('factual')) return 'reason-badge factual';
    if (reason.includes('summarization')) return 'reason-badge summarization';
    return 'reason-badge fallback';
  };

  return (
    <div className="chat-interface">
      <div className="header">
        <h1>LLM Smart Router</h1>
        <p>Test intelligent routing between LLaMA 3.2 models via Ollama (1B fast vs 3B creative)</p>
      </div>

      <form onSubmit={handleSubmit} className="chat-form">
        <div className="input-group">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Enter your message here..."
            rows={3}
            className="message-input"
            disabled={loading}
          />
        </div>

        <div className="controls">
          <div className="control-group">
            <label htmlFor="latency-hint">Latency Hint:</label>
            <select
              id="latency-hint"
              value={latencyHint}
              onChange={(e) => setLatencyHint(e.target.value as LatencyHint)}
              disabled={loading}
            >
              <option value="normal">Normal</option>
              <option value="fast">Fast</option>
            </select>
          </div>

          <div className="control-group">
            <label htmlFor="priority">Priority:</label>
            <select
              id="priority"
              value={priority}
              onChange={(e) => setPriority(e.target.value as Priority)}
              disabled={loading}
            >
              <option value="low">Low</option>
              <option value="normal">Normal</option>
              <option value="high">High</option>
            </select>
          </div>

          <button type="submit" disabled={loading || !message.trim()}>
            {loading ? 'Routing...' : 'Send Message'}
          </button>
        </div>
      </form>

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="responses">
        {responses.map((response, index) => (
          <div key={index} className="response-card">
            <div className="response-header">
              <span className={getModelBadgeClass(response.model_selected)}>
                {response.model_selected}
              </span>
              <span className={getReasonBadgeClass(response.meta.reason)}>
                {response.meta.reason}
              </span>
              <span className="latency-badge">
                {response.meta.latency_ms}ms
              </span>
              <span className="queue-badge">
                Queue: {response.meta.queue_depth}
              </span>
            </div>
            <div className="response-content">
              {response.completion}
            </div>
          </div>
        ))}
      </div>

      {responses.length === 0 && (
        <div className="empty-state">
          <p>Try different types of queries to see how the router chooses between models:</p>
          <ul>
            <li><strong>Creative:</strong> "Write a story about..." → LLaMA 3.2 1B Creative</li>
            <li><strong>Factual + Fast:</strong> "What is the capital of...?" → LLaMA 3.2 1B Fast</li>
            <li><strong>Summarization:</strong> "Summarize..." → Context-dependent</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;