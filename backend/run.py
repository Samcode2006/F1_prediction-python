"""
backend/run.py
Launches the FastAPI server with uvicorn.
Run from the project root: python backend/run.py
"""

import os
import sys

# Ensure project root is on path so predictor.py can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[os.path.dirname(os.path.dirname(os.path.abspath(__file__)))],
    )
