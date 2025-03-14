import pandas as pd
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import os
from typing import Dict, List

def load_dataset(file_path: str) -> pd.DataFrame:
    """Load and preprocess the dataset."""
    df = pd.read_csv(file_path)
    # Combine query and response into a single text
    df['text'] = df.apply(lambda row: f"Question: {row['Query']}\nAnswer: {row['Response']}", axis=1)
    return df

def prepare_dataset(df: pd.DataFrame, tokenizer: AutoTokenizer) -> Dataset:
    """Prepare the dataset for training."""
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
    
    # Convert DataFrame to HuggingFace Dataset
    dataset = Dataset.from_pandas(df)
    # Tokenize the dataset
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )
    return tokenized_dataset

def train_model(
    model_name: str = "microsoft/phi-2",
    dataset_path: str = "../dataset_banking_chatbot.csv",
    output_dir: str = "finetuned_model",
    num_train_epochs: int = 3,
    batch_size: int = 4,
    learning_rate: float = 2e-5
):
    """Train the model on the banking chatbot dataset."""
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # Load and prepare dataset
    df = load_dataset(dataset_path)
    dataset = prepare_dataset(df, tokenizer)
    
    # Split dataset into train and validation
    split_dataset = dataset.train_test_split(test_size=0.1)
    
    # Define training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        push_to_hub=False,
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=split_dataset["train"],
        eval_dataset=split_dataset["test"],
        data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
    )
    
    # Train the model
    trainer.train()
    
    # Save the model and tokenizer
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)
    
    print(f"Model saved to {output_dir}")

if __name__ == "__main__":
    train_model() 