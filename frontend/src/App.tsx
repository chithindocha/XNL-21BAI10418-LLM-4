import { useState, useEffect, useRef } from 'react'
import './App.css'

interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:7860/ws/chat');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('Connected to WebSocket');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.response) {
        addMessage(data.response, false);
      }
      setIsLoading(false);
    };

    ws.onclose = () => {
      console.log('Disconnected from WebSocket');
      setIsConnected(false);
      // Attempt to reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
  };

  const addMessage = (text: string, isUser: boolean) => {
    setMessages(prev => [...prev, { text, isUser, timestamp: new Date() }]);
    // Scroll to bottom after message is added
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !wsRef.current || !isConnected) return;

    addMessage(input, true);
    wsRef.current.send(JSON.stringify({
      message: input,
      user_id: 'default'
    }));
    setInput('');
    setIsLoading(true);
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>Financial Assistant</h1>
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </header>

      <div className="messages-container">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.isUser ? 'user-message' : 'bot-message'}`}
          >
            <div className="message-content">{msg.text}</div>
            <div className="message-timestamp">
              {msg.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message bot-message">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={!isConnected || isLoading}
        />
        <button type="submit" disabled={!isConnected || isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default App;
