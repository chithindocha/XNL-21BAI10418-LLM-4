// API configuration
const API_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend-url.com'  // Update this with your backend URL
  : 'http://localhost:8000';

// WebSocket configuration
const WS_URL = process.env.NODE_ENV === 'production'
  ? 'wss://your-backend-url.com'  // Update this with your backend WebSocket URL
  : 'ws://localhost:8000'; 