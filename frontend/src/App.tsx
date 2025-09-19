import { useEffect, useState } from 'react';
import ChatInterface from './components/ChatInterface';
import { llmRouterApi } from './services/api';
import './App.css';

function App() {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await llmRouterApi.getHealth();
        setIsHealthy(true);
      } catch (error) {
        setIsHealthy(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <div className="status-bar">
        <div className={`status-indicator ${isHealthy ? 'healthy' : 'unhealthy'}`}>
          {isHealthy === null ? '⏳ Checking...' :
           isHealthy ? 'Router Online' : 'Router Offline'}
        </div>
      </div>

      {isHealthy === false && (
        <div className="connection-error">
          <h3>⚠️ Connection Error</h3>
          <p>Cannot connect to the LLM Router API. Make sure the backend is running on port 8080.</p>
          <code>MOCK_MODE=true python main.py</code>
        </div>
      )}

      <ChatInterface />
    </div>
  );
}

export default App;