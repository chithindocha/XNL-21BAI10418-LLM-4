import subprocess
import sys
import os
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_backend():
    """Start the FastAPI backend server"""
    try:
        logger.info("Starting FastAPI backend server...")
        backend_process = subprocess.Popen(
            ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Wait for the server to start
        time.sleep(5)
        if backend_process.poll() is not None:
            logger.error("Backend server failed to start")
            sys.exit(1)
        logger.info("Backend server started successfully")
        return backend_process
    except Exception as e:
        logger.error(f"Error starting backend server: {e}")
        sys.exit(1)

def run_nginx():
    """Start the Nginx server"""
    try:
        logger.info("Starting Nginx server...")
        # Ensure Nginx has proper permissions
        subprocess.run(["sudo", "chown", "-R", "user:user", "/var/log/nginx"])
        subprocess.run(["sudo", "chown", "-R", "user:user", "/var/run"])
        
        # Start Nginx
        nginx_process = subprocess.Popen(
            ["nginx", "-g", "daemon off;"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Wait for Nginx to start
        time.sleep(2)
        if nginx_process.poll() is not None:
            logger.error("Nginx server failed to start")
            sys.exit(1)
        logger.info("Nginx server started successfully")
        return nginx_process
    except Exception as e:
        logger.error(f"Error starting Nginx server: {e}")
        sys.exit(1)

def main():
    """Main function to start all services"""
    try:
        # Set environment variables
        os.environ["MODEL_PATH"] = "/app/finetuned_model"
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        
        # Start backend server
        backend_process = run_backend()
        
        # Start Nginx server
        nginx_process = run_nginx()
        
        logger.info("All services started successfully")
        
        # Keep the main process running
        try:
            while True:
                time.sleep(1)
                # Check if any process has died
                if backend_process.poll() is not None:
                    logger.error("Backend server died unexpectedly")
                    sys.exit(1)
                if nginx_process.poll() is not None:
                    logger.error("Nginx server died unexpectedly")
                    sys.exit(1)
        except KeyboardInterrupt:
            logger.info("Shutting down services...")
            backend_process.terminate()
            nginx_process.terminate()
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 