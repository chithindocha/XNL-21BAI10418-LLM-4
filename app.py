import subprocess
import sys
import os
import time
import logging
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_model_directory():
    """Set up the model directory with a fallback model if needed"""
    try:
        app_root = Path(__file__).parent.absolute()
        model_path = app_root / "backend" / "finetuned_model"
        
        # Check if model directory exists and has required files
        if not model_path.exists() or not (model_path / "config.json").exists():
            logger.info("Model files not found, using fallback model: microsoft/DialoGPT-small")
            # Set environment variable to use the fallback model
            os.environ["USE_FALLBACK_MODEL"] = "true"
            os.environ["FALLBACK_MODEL"] = "microsoft/DialoGPT-small"
        else:
            logger.info("Using finetuned model from local directory")
            os.environ["USE_FALLBACK_MODEL"] = "false"
            
        return str(model_path)
    except Exception as e:
        logger.error(f"Error setting up model directory: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def run_backend():
    """Start the FastAPI backend server"""
    try:
        logger.info("Starting FastAPI backend server...")
        # Get absolute paths
        app_root = Path(__file__).parent.absolute()
        backend_path = app_root / "backend"
        
        # Add backend directory to Python path
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        # Log the Python path for debugging
        logger.info(f"Python path: {sys.path}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Backend path: {backend_path}")
        
        # List backend directory contents for debugging
        logger.info(f"Backend directory contents: {os.listdir(backend_path)}")
            
        # Start the backend server with output capture
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(backend_path),
            text=True,
            bufsize=1,
            universal_newlines=True,
            env={**os.environ, "PYTHONPATH": f"{str(backend_path)}:{os.environ.get('PYTHONPATH', '')}"}
        )
        
        # Monitor the startup
        start_time = time.time()
        while time.time() - start_time < 30:  # Increased timeout to 30 seconds
            if backend_process.poll() is not None:
                # Process died, get the error message
                stdout, stderr = backend_process.communicate()
                logger.error(f"Backend server failed to start")
                logger.error(f"Stdout: {stdout}")
                logger.error(f"Stderr: {stderr}")
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
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
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
                stdout, stderr = nginx_process.communicate()
                logger.error(f"Nginx server failed to start")
                logger.error(f"Stdout: {stdout}")
                logger.error(f"Stderr: {stderr}")
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
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def main():
    """Main function to start all services"""
    try:
        # Set up model directory and environment variables
        model_path = setup_model_directory()
        os.environ["MODEL_PATH"] = model_path
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        
        # Log environment for debugging
        logger.info(f"Environment variables:")
        logger.info(f"MODEL_PATH: {os.environ.get('MODEL_PATH')}")
        logger.info(f"USE_FALLBACK_MODEL: {os.environ.get('USE_FALLBACK_MODEL')}")
        logger.info(f"FALLBACK_MODEL: {os.environ.get('FALLBACK_MODEL')}")
        logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
        logger.info(f"Current directory: {os.getcwd()}")
        
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
                    logger.error(f"Backend server died unexpectedly")
                    logger.error(f"Stdout: {stdout}")
                    logger.error(f"Stderr: {stderr}")
                    sys.exit(1)
                    
                if nginx_process.poll() is not None:
                    stdout, stderr = nginx_process.communicate()
                    logger.error(f"Nginx server died unexpectedly")
                    logger.error(f"Stdout: {stdout}")
                    logger.error(f"Stderr: {stderr}")
                    sys.exit(1)
                    
            except KeyboardInterrupt:
                logger.info("Shutting down services...")
                backend_process.terminate()
                nginx_process.terminate()
                sys.exit(0)
            
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 