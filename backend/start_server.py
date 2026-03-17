#!/usr/bin/env python3
"""
Simple startup script for Atiende24 backend server
"""
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Now import and run the server
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting Atiende24 Backend Server...")
    print(f"📁 Backend directory: {backend_dir}")
    print(f"🌐 Server will be available at: http://localhost:8000")
    print("📚 API documentation: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )