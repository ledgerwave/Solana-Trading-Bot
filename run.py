#!/usr/bin/env python3
"""
Entry point for running the Solana Copy Trading Bot.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.main import app
from app.core.bot_manager import BotManager
from app.api.endpoints import set_bot_manager

async def main():
    """Main entry point."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('bot.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Solana Copy Trading Bot...")
    
    try:
        # Initialize bot manager
        bot_manager = BotManager()
        await bot_manager.initialize()
        
        # Set bot manager in API endpoints
        set_bot_manager(bot_manager)
        
        # Start the FastAPI application
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        if 'bot_manager' in locals():
            await bot_manager.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            # Handle the case where we're already in an event loop
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.run(main())
        else:
            raise
