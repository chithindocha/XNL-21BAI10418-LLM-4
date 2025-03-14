import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.chat_service import ChatService
from app.models.chat import ChatMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Financial Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chat service
try:
    logger.info("Initializing chat service...")
    chat_service = ChatService()
    logger.info("Chat service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize chat service: {str(e)}")
    raise

@app.on_event("startup")
async def startup_event():
    try:
        # Log environment information
        logger.info("Environment variables:")
        logger.info(f"MODEL_PATH: {os.environ.get('MODEL_PATH')}")
        logger.info(f"USE_FALLBACK_MODEL: {os.environ.get('USE_FALLBACK_MODEL')}")
        logger.info(f"FALLBACK_MODEL: {os.environ.get('FALLBACK_MODEL')}")
        logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
        
        # Log directory information
        current_dir = os.getcwd()
        logger.info(f"Current directory: {current_dir}")
        backend_path = str(Path(current_dir) / "backend")
        logger.info(f"Backend path: {backend_path}")
        
        if os.path.exists(backend_path):
            logger.info(f"Backend directory contents: {os.listdir(backend_path)}")
        
        logger.info("Starting FastAPI backend server...")
        logger.info(f"Python path: {sys.path}")
        logger.info(f"Current working directory: {os.getcwd()}")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {"status": "healthy", "model_loaded": True}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    try:
        await websocket.accept()
        logger.info("WebSocket connection established")
        
        while True:
            try:
                # Receive message
                data = await websocket.receive_json()
                message = data.get("message", "")
                user_id = data.get("user_id", "default")
                
                logger.info(f"Received message from user {user_id}: {message[:50]}...")
                
                # Generate response
                response = await chat_service.get_response(message, user_id)
                
                # Send response
                await websocket.send_json({"response": response})
                logger.info(f"Sent response to user {user_id}")
                
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}")
                await websocket.send_json({
                    "error": "An error occurred while processing your message. Please try again."
                })
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()

@app.post("/chat")
async def chat(message: ChatMessage):
    """HTTP endpoint for chat (fallback for WebSocket)"""
    try:
        response = await chat_service.get_response(message.message, message.user_id)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 