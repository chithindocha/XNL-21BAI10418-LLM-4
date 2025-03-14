import subprocess
import sys
import os
import time
from pathlib import Path

def run_backend():
    """Run the FastAPI backend server"""
    backend_dir = Path("backend")
    os.chdir(backend_dir)
    subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])

def run_nginx():
    """Start Nginx server"""
    subprocess.Popen(["nginx", "-g", "daemon off;"])

def main():
    # Set environment variables
    os.environ["MODEL_PATH"] = "/app/finetuned_model"
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    
    # Start backend server
    print("Starting backend server...")
    run_backend()
    
    # Wait for backend to start
    time.sleep(5)
    
    # Start Nginx
    print("Starting Nginx server...")
    run_nginx()
    
    # Keep the main process running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main() 