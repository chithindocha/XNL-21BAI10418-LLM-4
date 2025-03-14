---
title: Financial Assistant Chatbot
emoji: 💬
colorFrom: blue
colorTo: indigo
sdk: docker
sdk_version: "3.8"
app_port: 7860
app_file: app.py
pinned: false
---

# Financial Chatbot with DialoGPT

A sophisticated financial chatbot built with FastAPI, React, and DialoGPT. The chatbot provides banking and financial assistance through a modern web interface.

[![Sync to Hugging Face Spaces](https://github.com/YOUR_USERNAME/XNL-21BAI10418-LLM-4/actions/workflows/sync.yml/badge.svg)](https://github.com/YOUR_USERNAME/XNL-21BAI10418-LLM-4/actions/workflows/sync.yml)

## Features

- 🤖 Advanced language model using DialoGPT
- 🚀 FastAPI backend for high performance
- ⚛️ Modern React frontend with Material-UI
- 🔄 Real-time chat interface with WebSocket support
- 🎨 Responsive and intuitive UI design
- 🔒 Secure deployment configuration
- 🔄 Automatic sync between GitHub and Hugging Face Spaces

## Live Demo

Try the live demo on Hugging Face Spaces: [Financial Chatbot Demo](https://huggingface.co/spaces/Chit1324/XNL-21BAI10418-LLM-4)

## Tech Stack

- **Backend**:
  - FastAPI
  - Python 3.10+
  - Transformers (DialoGPT)
  - WebSocket support
  - Nginx

- **Frontend**:
  - React
  - Material-UI
  - Framer Motion
  - TypeScript

- **Deployment**:
  - Docker
  - Hugging Face Spaces
  - GitHub Actions

## Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/XNL-21BAI10418-LLM-4.git
   cd XNL-21BAI10418-LLM-4
   ```

2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

4. Start the development servers:
   ```bash
   # Terminal 1 - Backend
   cd backend
   python -m uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

## Deployment

The project is automatically deployed to Hugging Face Spaces when changes are pushed to the main branch. The deployment process is handled by GitHub Actions.

### Setting up GitHub Actions

1. Generate a Hugging Face token from your [Hugging Face account settings](https://huggingface.co/settings/tokens)
2. Add the token as a secret named `HF_TOKEN` in your GitHub repository settings
3. Push changes to the main branch to trigger automatic deployment

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Hugging Face](https://huggingface.co/) for the model hosting and Spaces platform
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent API framework
- [React](https://reactjs.org/) for the frontend framework
- [Material-UI](https://mui.com/) for the UI components

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