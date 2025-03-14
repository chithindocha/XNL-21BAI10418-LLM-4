import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import pandas as pd
import logging
from dotenv import load_dotenv
import os
import shutil
import time
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('training.log')
    ]
)
logger = logging.getLogger(__name__)

def prepare_dataset():
    """Load and prepare the dataset from CSV file."""
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv('Dataset_Banking_chatbot.csv', encoding=encoding)
                logger.info(f"Successfully read CSV with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise ValueError("Could not read CSV file with any encoding")
        
        # Convert to UTF-8 and save
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/banking_chatbot_utf8.csv', index=False, encoding='utf-8')
        
        # Create dataset with proper formatting
        dataset = Dataset.from_pandas(df)
        
        # Split into train and validation
        split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
        
        return split_dataset
    except Exception as e:
        logger.error(f"Error preparing dataset: {str(e)}")
        raise

def tokenize_function(examples, tokenizer):
    """Tokenize the examples with proper formatting."""
    try:
        # Format the conversation
        formatted_examples = []
        for q, a in zip(examples['Query'], examples['Response']):
            # Create a structured conversation format
            conversation = f"""<|user|>
{q}</s>
<|assistant|>
{a}</s>"""
            formatted_examples.append(conversation)
        
        # Tokenize with proper padding and truncation
        tokenized = tokenizer(
            formatted_examples,
            padding="max_length",
            truncation=True,
            max_length=512,  # Increased for Zephyr's context window
            return_tensors="pt"
        )
        
        return tokenized
    except Exception as e:
        logger.error(f"Error in tokenization: {str(e)}")
        raise

def save_model_safely(model, tokenizer, save_dir, max_retries=3):
    """Safely save the model and tokenizer with retry logic."""
    temp_dir = f"{save_dir}_temp_{int(time.time())}"
    final_dir = save_dir
    
    for attempt in range(max_retries):
        try:
            # First save to a temporary directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)
            
            # Save model and tokenizer to temp directory
            model.save_pretrained(temp_dir)
            tokenizer.save_pretrained(temp_dir)
            
            # If successful, move to final location
            if os.path.exists(final_dir):
                shutil.rmtree(final_dir)
            shutil.move(temp_dir, final_dir)
            
            logger.info(f"Successfully saved model to {final_dir}")
            return True
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed to save model: {str(e)}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            time.sleep(1)  # Wait before retrying
    
    raise RuntimeError(f"Failed to save model after {max_retries} attempts")

def main():
    """Main training function."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        # Initialize model and tokenizer
        model_name = "HuggingFaceH4/zephyr-7b-beta"
        logger.info(f"Loading model and tokenizer from {model_name}")
        
        # Load model with memory optimizations
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto",
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            use_cache=False  # Disable KV cache for training
        )
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        
        # Prepare dataset
        logger.info("Preparing dataset...")
        dataset = prepare_dataset()
        
        # Tokenize datasets
        logger.info("Tokenizing datasets...")
        def tokenize(examples):
            return tokenize_function(examples, tokenizer)
        
        tokenized_datasets = dataset.map(
            tokenize,
            batched=True,
            remove_columns=dataset["train"].column_names
        )
        
        # Training arguments with memory optimizations
        training_args = TrainingArguments(
            output_dir="./finetuned_model",
            num_train_epochs=2,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=16,
            learning_rate=2e-5,
            weight_decay=0.01,
            warmup_steps=50,
            logging_steps=5,
            save_steps=50,
            eval_steps=50,
            evaluation_strategy="steps",
            load_best_model_at_end=True,
            push_to_hub=False,
            fp16=True if device == "cuda" else False,
            gradient_checkpointing=True if device == "cuda" else False,
            optim="adamw_torch",
            report_to="none",
            remove_unused_columns=True,
            dataloader_pin_memory=True if device == "cuda" else False,
            max_grad_norm=1.0,
            lr_scheduler_type="cosine"
        )
        
        # Initialize trainer
        logger.info("Initializing trainer...")
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["test"],
            data_collator=DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False
            )
        )
        
        # Train the model
        logger.info("Starting training...")
        trainer.train()
        
        # Save the model and tokenizer safely
        logger.info("Saving model and tokenizer...")
        save_model_safely(model, tokenizer, "./finetuned_model")
        
        logger.info("Training completed successfully")
        
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        raise

if __name__ == "__main__":
    main() 