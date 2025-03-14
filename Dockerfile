# Use CUDA base image for GPU support
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PATH=/home/user/.local/bin:$PATH

# Create a new user with ID 1000
RUN useradd -m -u 1000 user

# Install system dependencies and Node.js 20
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@10.2.4

# Switch to the user
USER user

# Set home directory
ENV HOME=/home/user

# Set working directory
WORKDIR $HOME/app

# Copy requirements first to leverage Docker cache
COPY --chown=user backend/requirements.txt $HOME/app/backend/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r $HOME/app/backend/requirements.txt

# Copy the rest of the application
COPY --chown=user . $HOME/app/

# Create necessary directories with proper permissions
RUN mkdir -p $HOME/app/backend/data \
    && mkdir -p $HOME/app/backend/finetuned_model \
    && mkdir -p $HOME/app/frontend/node_modules

# Install frontend dependencies
WORKDIR $HOME/app/frontend
RUN npm install

# Build frontend
RUN npm run build

# Set up Nginx for serving frontend
USER root
RUN apt-get update && apt-get install -y nginx \
    && mkdir -p /var/log/nginx \
    && mkdir -p /var/run \
    && chown -R user:user /var/log/nginx \
    && chown -R user:user /var/run \
    && chown -R user:user /etc/nginx/conf.d
USER user

# Copy Nginx configuration
COPY --chown=user nginx.conf /etc/nginx/conf.d/default.conf

# Expose ports
EXPOSE 7860 8000

# Set environment variables
ENV MODEL_PATH=/app/finetuned_model \
    CUDA_VISIBLE_DEVICES=0

# Set working directory back to app root
WORKDIR $HOME/app

# Start the application
CMD ["python3", "app.py"] 