from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from collections import deque
import os

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        try:
            # Check if we should use fallback model
            use_fallback = os.environ.get("USE_FALLBACK_MODEL", "false").lower() == "true"
            fallback_model = os.environ.get("FALLBACK_MODEL", "microsoft/DialoGPT-small")
            model_path = os.environ.get("MODEL_PATH", "finetuned_model")

            # Log device information
            logger.info(f"CUDA available: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                logger.info(f"CUDA device: {torch.cuda.get_device_name(0)}")
            
            # Set device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")

            if use_fallback:
                logger.info(f"Using fallback model: {fallback_model}")
                try:
                    logger.info("Loading tokenizer...")
                    self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
                    logger.info("Tokenizer loaded successfully")
                    
                    logger.info("Loading model...")
                    self.model = AutoModelForCausalLM.from_pretrained(
                        fallback_model,
                        torch_dtype=torch.float32,
                        low_cpu_mem_usage=True
                    )
                    self.model = self.model.to(device)
                    logger.info("Model loaded successfully")
                except Exception as e:
                    logger.error(f"Error loading fallback model: {str(e)}")
                    raise
            else:
                logger.info(f"Loading model from: {model_path}")
                try:
                    logger.info("Loading tokenizer...")
                    self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                    logger.info("Tokenizer loaded successfully")
                    
                    logger.info("Loading model...")
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_path,
                        torch_dtype=torch.float32,
                        low_cpu_mem_usage=True
                    )
                    self.model = self.model.to(device)
                    logger.info("Model loaded successfully")
                except Exception as e:
                    logger.error(f"Error loading local model: {str(e)}")
                    raise
                
            # Initialize conversation history
            self.conversation_history = {}
            self.max_history = 5
            logger.info("Chat service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing chat service: {str(e)}")
            raise

    def _get_conversation_context(self, user_id: str) -> str:
        """Get the conversation history for a user."""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = deque(maxlen=self.max_history)
        
        history = self.conversation_history[user_id]
        if not history:
            return ""
        
        context = "Previous conversation:\n"
        for q, a in history:
            context += f"User: {q}\nAssistant: {a}\n"
        return context

    def _update_conversation_history(self, user_id: str, question: str, answer: str):
        """Update the conversation history for a user."""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = deque(maxlen=self.max_history)
        self.conversation_history[user_id].append((question, answer))

    async def get_response(self, message: str, user_id: str) -> str:
        try:
            # Get conversation history
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = deque(maxlen=self.max_history)
            
            # Prepare input
            conversation = list(self.conversation_history[user_id])
            context = ""
            for prev_msg, prev_resp in conversation:
                context += f"User: {prev_msg}\nAssistant: {prev_resp}\n"
            context += f"User: {message}\nAssistant:"
            
            logger.info(f"Generating response for input: {message[:50]}...")
            
            # Tokenize input
            inputs = self.tokenizer(context, return_tensors="pt").to(self.model.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=512,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.2
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.replace(context, "").strip()
            
            # Update conversation history
            self.conversation_history[user_id].append((message, response))
            
            logger.info(f"Generated response: {response[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Could you please try again?"

    async def process_message(
        self,
        message: str,
        user_id: str,
        context: Optional[List[Dict]] = None
    ) -> Dict:
        """Process a message and return a response."""
        try:
            # Generate response using the model
            response = await self.get_response(message, user_id)
            
            return {
                "message": response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "message": "I apologize, but I'm having trouble processing your request. Please try again later. I'm here to help!",
                "timestamp": datetime.now().isoformat()
            } 