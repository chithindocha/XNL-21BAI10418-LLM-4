import socketio
from typing import Dict, Any
from app.core.config import settings

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['http://localhost:5173'],
    logger=True,
    engineio_logger=True
)

# Store active connections
active_connections: Dict[str, Any] = {}

@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    print(f"Client connected: {sid}")
    active_connections[sid] = {
        "connected_at": datetime.utcnow(),
        "last_activity": datetime.utcnow()
    }

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    print(f"Client disconnected: {sid}")
    if sid in active_connections:
        del active_connections[sid]

@sio.event
async def chat_message(sid, data):
    """Handle incoming chat messages"""
    try:
        # Update last activity
        if sid in active_connections:
            active_connections[sid]["last_activity"] = datetime.utcnow()
        
        # Process message and get response
        response = await process_chat_message(data)
        
        # Send response back to client
        await sio.emit('chat_response', {
            'message': response,
            'timestamp': datetime.utcnow().isoformat()
        }, room=sid)
        
    except Exception as e:
        # Handle errors gracefully
        await sio.emit('error', {
            'message': 'An error occurred while processing your message',
            'details': str(e)
        }, room=sid)

async def process_chat_message(data: Dict[str, Any]) -> str:
    """Process chat message and generate response"""
    # TODO: Implement message processing logic
    # This will integrate with the LLM and vector database
    return "Message received and processed"

# Heartbeat mechanism
async def check_connections():
    """Periodically check and clean up inactive connections"""
    while True:
        current_time = datetime.utcnow()
        inactive_sids = []
        
        for sid, connection in active_connections.items():
            if (current_time - connection["last_activity"]).seconds > settings.WS_HEARTBEAT_INTERVAL * 2:
                inactive_sids.append(sid)
        
        for sid in inactive_sids:
            await sio.disconnect(sid)
        
        await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL) 