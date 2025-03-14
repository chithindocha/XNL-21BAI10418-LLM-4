FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend /app/backend
COPY frontend/dist /app/frontend/build

# Set environment variables
ENV PYTHONPATH=/app
ENV MODEL_PATH=/app/backend/finetuned_model
ENV USE_FALLBACK_MODEL=true
ENV FALLBACK_MODEL=microsoft/DialoGPT-small

# Expose port
EXPOSE 7860

# Set the command to run the application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "7860"] 