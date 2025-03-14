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

            if use_fallback:
                logger.info(f"Using fallback model: {fallback_model}")
                self.model = AutoModelForCausalLM.from_pretrained(fallback_model)
                self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            else:
                logger.info(f"Loading model from: {model_path}")
                self.model = AutoModelForCausalLM.from_pretrained(model_path)
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            # Fallback to DialoGPT if there's an error
            logger.info("Falling back to DialoGPT-small model")
            self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")

        self.conversation_history = {}  # Store conversations by user_id
        self.max_history = 5  # Keep last 5 exchanges

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
        """Generate a response using the model."""
        try:
            # Get conversation history
            history = self._get_conversation_context(user_id)
            
            # Prepare the input prompt with context and personality
            prompt = f"""You are FinBot, a friendly and professional banking assistant with a warm personality. You have expertise in banking, finance, and customer service. You always maintain a helpful and courteous tone while providing accurate information.

Your key traits:
- Professional yet approachable
- Clear and concise in explanations
- Patient and understanding
- Proactive in offering relevant information
- Always maintains a positive tone
- Uses a conversational style while remaining professional
- Provides specific, actionable advice when possible

{history}

Current conversation:
User: {message}

FinBot:"""
            
            # Generate response with optimized parameters
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            outputs = self.model.generate(
                **inputs,
                max_length=512,  # Increased for more detailed responses
                num_return_sequences=1,
                temperature=0.8,  # Slightly increased for more creativity
                top_p=0.95,  # Increased for more diverse responses
                top_k=50,  # Added top_k sampling
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.3,  # Increased to prevent repetition
                no_repeat_ngram_size=3,  # Prevent repetition of phrases
                num_beams=4,  # Added beam search
                early_stopping=True,  # Now valid with beam search
                length_penalty=1.1,  # Now valid with beam search
                min_length=20,  # Ensure minimum response length
                max_new_tokens=256  # Control new token generation
            )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the answer part
            response = response.split("FinBot:")[-1].strip()
            
            # Clean up and enhance the response
            response = response.replace("\n", " ").strip()
            
            # Add personality and handle edge cases
            if not response:
                response = "I apologize, but I'm not sure how to respond to that. Could you please rephrase your question? I'm here to help!"
            elif response.lower().startswith(("i don't know", "i am not sure", "i'm not sure")):
                response = "I apologize, but I'm not entirely sure about that. Could you please provide more details or rephrase your question? I want to make sure I give you the most accurate information."
            elif len(response.split()) < 5:  # If response is too short
                response = "I understand your question, but I'd like to provide more detailed information. " + response
            
            # Add conversational elements
            if not response.lower().startswith(("i apologize", "i understand", "thank you", "please")):
                response = "I understand your question. " + response
            
            # Update conversation history
            self._update_conversation_history(user_id, message, response)
            
            return response
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response at the moment. Please try again later. I'm here to help!"

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