from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.services.chat_service import ChatService
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
chat_service = ChatService()

@app.get("/")
async def root():
    return {"message": "Financial Chatbot API is running"}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        logger.info("connection open")
        
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                logger.info(f"Received message: {data}")
                
                # Parse JSON message
                message_data = json.loads(data)
                user_message = message_data.get("text", "")
                
                # Process message
                response = await chat_service.process_message(
                    message=user_message,
                    user_id="user",  # You might want to implement proper user identification
                    context=None
                )
                
                # Send response
                await websocket.send_json(response)
                
            except WebSocketDisconnect:
                logger.info("Client disconnected")
                break
            except json.JSONDecodeError:
                logger.error("Invalid JSON message received")
                await websocket.send_json({
                    "message": "Invalid message format. Please send a JSON message with a 'text' field.",
                    "timestamp": None
                })
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await websocket.send_json({
                    "message": "An error occurred while processing your message. Please try again.",
                    "timestamp": None
                })
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        try:
            await websocket.close()
        except:
            pass  # Ignore errors when closing an already closed connection 