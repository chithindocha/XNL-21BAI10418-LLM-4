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
        # Add backend directory to Python path
        backend_path = str(Path(__file__).parent / "backend")
        if backend_path not in sys.path:
            sys.path.append(backend_path)
            
        # Start the backend server with output capture
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=backend_path,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Monitor the startup
        start_time = time.time()
        while time.time() - start_time < 10:  # Wait up to 10 seconds
            if backend_process.poll() is not None:
                # Process died, get the error message
                _, stderr = backend_process.communicate()
                logger.error(f"Backend server failed to start with error: {stderr}")
                sys.exit(1)
                
            # Check stdout/stderr for startup progress
            stderr = backend_process.stderr.readline()
            if stderr:
                logger.info(f"Backend startup: {stderr.strip()}")
            
            stdout = backend_process.stdout.readline()
            if stdout:
                logger.info(f"Backend startup: {stdout.strip()}")
                if "Application startup complete" in stdout:
                    logger.info("Backend server started successfully")
                    return backend_process
                
            time.sleep(0.1)
            
        logger.error("Backend server startup timed out")
        backend_process.terminate()
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Error starting backend server: {str(e)}")
        sys.exit(1)

def run_nginx():
    """Start the Nginx server"""
    try:
        logger.info("Starting Nginx server...")
        # Start Nginx without sudo (since we already set permissions in Dockerfile)
        nginx_process = subprocess.Popen(
            ["nginx", "-g", "daemon off;"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Monitor the startup
        start_time = time.time()
        while time.time() - start_time < 5:  # Wait up to 5 seconds
            if nginx_process.poll() is not None:
                # Process died, get the error message
                _, stderr = nginx_process.communicate()
                logger.error(f"Nginx server failed to start with error: {stderr}")
                sys.exit(1)
                
            # Check stderr for any errors
            stderr = nginx_process.stderr.readline()
            if stderr:
                logger.error(f"Nginx startup error: {stderr.strip()}")
                nginx_process.terminate()
                sys.exit(1)
                
            time.sleep(0.1)
            
        logger.info("Nginx server started successfully")
        return nginx_process
        
    except Exception as e:
        logger.error(f"Error starting Nginx server: {str(e)}")
        sys.exit(1)

def main():
    """Main function to start all services"""
    try:
        # Set environment variables
        os.environ["MODEL_PATH"] = str(Path(__file__).parent / "backend" / "finetuned_model")
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        
        # Start backend server
        backend_process = run_backend()
        
        # Start Nginx server
        nginx_process = run_nginx()
        
        logger.info("All services started successfully")
        
        # Keep the main process running and monitor child processes
        while True:
            try:
                time.sleep(1)
                # Check if any process has died
                if backend_process.poll() is not None:
                    stdout, stderr = backend_process.communicate()
                    logger.error(f"Backend server died unexpectedly. Error: {stderr}")
                    sys.exit(1)
                    
                if nginx_process.poll() is not None:
                    stdout, stderr = nginx_process.communicate()
                    logger.error(f"Nginx server died unexpectedly. Error: {stderr}")
                    sys.exit(1)
                    
            except KeyboardInterrupt:
                logger.info("Shutting down services...")
                backend_process.terminate()
                nginx_process.terminate()
                sys.exit(0)
            
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 