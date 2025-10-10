"""
Solana Copy Trading Bot - FastAPI Application
Main application entry point with API endpoints for bot management.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import List, Dict, Any

from .core.bot_manager import BotManager
from .core.solana_client import SolanaClient
from .models.schemas import (
    BotStatus,
    WalletConfig,
    TransactionInfo,
    BotConfig,
    CopyTradingStats
)
from .api.endpoints import router
from .config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global bot manager instance
bot_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    global bot_manager

    # Startup
    logger.info("Starting Solana Copy Trading Bot...")
    bot_manager = BotManager()
    await bot_manager.initialize()

    # Set bot manager in API endpoints
    from .api.endpoints import set_bot_manager
    set_bot_manager(bot_manager)

    yield

    # Shutdown
    logger.info("Shutting down Solana Copy Trading Bot...")
    if bot_manager:
        await bot_manager.shutdown()

# Create FastAPI app
app = FastAPI(
    title="Solana Copy Trading Bot",
    description="Real-time Solana wallet monitoring and copy trading bot",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "Solana Copy Trading Bot API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "bot_running": bot_manager.is_running if bot_manager else False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level="info"
    )
