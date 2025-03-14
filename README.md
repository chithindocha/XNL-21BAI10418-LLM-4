# Financial Assistant Chatbot

A modern, responsive chatbot application for financial queries and assistance, built with React, FastAPI, and the Zephyr-7B language model.

## Features

- 🤖 Intelligent financial assistance using fine-tuned Zephyr-7B model
- 💬 Real-time chat interface with WebSocket support
- 🎨 Modern, responsive UI with Material-UI and Framer Motion
- 🌙 Light/Dark theme support
- 📱 Mobile-friendly design
- ⚡ Fast and efficient message handling
- 🔄 Automatic reconnection handling
- 📝 Message history with clear chat functionality

## Tech Stack

### Frontend
- React 18 with TypeScript
- Material-UI for components
- Framer Motion for animations
- WebSocket for real-time communication
- Vite for fast development and building

### Backend
- FastAPI for the web server
- WebSocket support for real-time chat
- Zephyr-7B language model
- Hugging Face Transformers
- Python 3.10+

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- CUDA-capable GPU (recommended for model inference)
- Docker and Docker Compose (optional, for containerized deployment)

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── services/
│   │   │   └── chat_service.py  # Chat service implementation
│   │   └── models/
│   │       └── chat.py       # Data models
│   ├── data/                 # Training data
│   ├── finetuned_model/      # Fine-tuned model files
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Backend container configuration
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   └── App.tsx         # Main application component
│   ├── package.json         # Node.js dependencies
│   └── Dockerfile          # Frontend container configuration
├── docker-compose.yml       # Docker services configuration
└── README.md               # This file
```

## Installation

### Backend Setup

1. Create and activate a Python virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download the fine-tuned model (if not already present):
```bash
# The model will be downloaded automatically when running the application
```

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

## Running the Application

### Development Mode

1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Production Mode

Using Docker Compose:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:80
- Backend API: http://localhost:8000

## Deployment to Hugging Face Spaces

1. Create a new Space on Hugging Face:
   - Go to https://huggingface.co/spaces
   - Click "New Space"
   - Choose "Docker" as the SDK
   - Set the Space name and visibility

2. Configure the Space:
   - Set the following environment variables in Space Settings:
     ```
     MODEL_PATH=/app/finetuned_model
     CUDA_VISIBLE_DEVICES=0
     ```

3. Push your code to the Space:
```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit"

# Add Hugging Face Space as remote
git remote add space https://huggingface.co/spaces/Chit1324/XNL-21BAI10418-LLM-4

# Push to Hugging Face
git push space main
```

4. Monitor the deployment:
   - Go to your Space's "Settings" tab
   - Check the "Deployment" section for build logs
   - Monitor the "Runtime" section for any errors

5. Access your application:
   - Once deployed, your app will be available at:
     ```
     https://Chit1324-XNL-21BAI10418-LLM-4.hf.space
     ```

## API Endpoints

### WebSocket
- `ws://localhost:8000/ws/chat` - WebSocket endpoint for real-time chat

### REST API
- `GET /api/health` - Health check endpoint
- `POST /api/chat` - HTTP endpoint for chat (fallback)

## Environment Variables

### Backend
- `MODEL_PATH` - Path to the fine-tuned model
- `CUDA_VISIBLE_DEVICES` - GPU device to use (default: 0)

### Frontend
- `VITE_API_URL` - Backend API URL (default: http://localhost:8000)

## Development

### Code Style

- Backend: Follow PEP 8 guidelines
- Frontend: Use ESLint and Prettier

### Running Tests

Backend:
```bash
cd backend
pytest
```

Frontend:
```bash
cd frontend
npm test
```

## Deployment

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. For production, use:
```bash
docker-compose -f docker-compose.prod.yml up --build
```

### Manual Deployment

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. Start the backend server:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

3. Serve the frontend build files using a web server (e.g., nginx)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Zephyr-7B](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta) - The base language model
- [FastAPI](https://fastapi.tiangolo.com/) - The web framework
- [React](https://reactjs.org/) - The frontend library
- [Material-UI](https://mui.com/) - The UI component library