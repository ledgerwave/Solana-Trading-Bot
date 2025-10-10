#!/usr/bin/env python3
"""
Simple startup script for the Solana Copy Trading Bot.
"""

import uvicorn
import logging
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    print("🚀 Starting Solana Copy Trading Bot...")
    print(f"📡 API will be available at: http://localhost:{settings.api_port}")
    print(f"📚 API documentation at: http://localhost:{settings.api_port}/docs")
    print("🛑 Press Ctrl+C to stop the bot")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level="info"
    )
