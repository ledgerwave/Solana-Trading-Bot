"""
FastAPI endpoints for the Solana Copy Trading Bot.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional
import logging

from ..models.schemas import (
    BotStatusResponse,
    AddWalletRequest,
    UpdateWalletRequest,
    TransactionHistoryResponse,
    WalletConfig,
    ErrorResponse
)
from ..core.bot_manager import BotManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Global bot manager instance (will be injected)
bot_manager: Optional[BotManager] = None

def set_bot_manager(manager: BotManager):
    """Set the bot manager instance."""
    global bot_manager
    bot_manager = manager

@router.get("/status", response_model=BotStatusResponse)
async def get_bot_status():
    """Get current bot status and statistics."""
    if not bot_manager:
        raise HTTPException(status_code=503, detail="Bot manager not initialized")
    
    return bot_manager.get_status()

@router.post("/start")
async def start_bot(background_tasks: BackgroundTasks):
    """Start the copy trading bot."""
    if not bot_manager:
        raise HTTPException(status_code=503, detail="Bot manager not initialized")
    
    try:
        await bot_manager.start_monitoring()
        return {"message": "Bot started successfully", "status": "running"}
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start bot: {str(e)}")

@router.post("/stop")
async def stop_bot():
    """Stop the copy trading bot."""
    if not bot_manager:
        raise HTTPException(status_code=503, detail="Bot manager not initialized")
    
    try:
        await bot_manager.stop_monitoring()
        return {"message": "Bot stopped successfully", "status": "stopped"}
    except Exception as e:
        logger.error(f"Failed to stop bot: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop bot: {str(e)}")

@router.get("/wallets", response_model=List[WalletConfig])
async def get_monitored_wallets():
    """Get list of monitored wallets."""
    if not bot_manager:
        raise HTTPException(status_code=503, detail="Bot manager not initialized")
    
    return list(bot_manager.monitored_wallets.values())

@router.post("/wallets", response_model=WalletConfig)
async def add_wallet(wallet_request: AddWalletRequest):
    """Add a wallet to monitoring."""
    if not bot_manager:
        raise HTTPException(status_code=503, detail="Bot manager not initialized")
    
    try:
        wallet_config = WalletConfig(
            address=wallet_request.address,
            enabled=wallet_request.enabled,
            copy_sol=wallet_request.copy_sol,
            copy_spl=wallet_request.copy_spl,
            copy_swaps=wallet_request.copy_swaps,
            max_amount=wallet_request.max_amount
        )
        
        await bot_manager.add_wallet(wallet_config)
        return wallet_config
    except Exception as e:
        logger.error(f"Failed to add wallet: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add wallet: {str(e)}")

@router.put("/wallets/{wallet_address}")
async def update_wallet(wallet_address: str, updates: UpdateWalletRequest):
    """Update wallet configuration."""
    if not bot_manager:
        raise HTTPException(status_code=503, detail="Bot manager not initialized")
    
    try:
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}
        await bot_manager.update_wallet(wallet_address, update_dict)
        return {"message": f"Wallet {wallet_address} updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update wallet: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update wallet: {str(e)}")

@router.delete("/wallets/{wallet_address}")
async def remove_wallet(wallet_address: str):
    """Remove a wallet from monitoring."""
    if not bot_manager:
        raise HTTPException(status_code=503, detail="Bot manager not initialized")
    
    try:
        await bot_manager.remove_wallet(wallet_address)
        return {"message": f"Wallet {wallet_address} removed successfully"}
    except Exception as e:
        logger.error(f"Failed to remove wallet: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to remove wallet: {str(e)}")

@router.get("/transactions", response_model=TransactionHistoryResponse)
async def get_transaction_history(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Get transaction history."""
    if not bot_manager:
        raise HTTPException(status_code=503, detail="Bot manager not initialized")
    
    try:
        transactions = bot_manager.get_transaction_history(limit, offset)
        return TransactionHistoryResponse(
            transactions=transactions,
            total_count=len(bot_manager.transaction_history),
            page=offset // limit + 1,
            page_size=limit
        )
    except Exception as e:
        logger.error(f"Failed to get transaction history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get transaction history: {str(e)}")

@router.get("/stats")
async def get_trading_stats():
    """Get copy trading statistics."""
    if not bot_manager:
        raise HTTPException(status_code=503, detail="Bot manager not initialized")
    
    return bot_manager.get_stats()

@router.get("/wallets/{wallet_address}/balance")
async def get_wallet_balance(wallet_address: str):
    """Get SOL balance for a wallet."""
    if not bot_manager:
        raise HTTPException(status_code=503, detail="Bot manager not initialized")
    
    try:
        balance = await bot_manager.solana_client.get_balance(wallet_address)
        return {"address": wallet_address, "balance": balance}
    except Exception as e:
        logger.error(f"Failed to get wallet balance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get wallet balance: {str(e)}")

@router.get("/bot/balance")
async def get_bot_balance():
    """Get bot wallet SOL balance."""
    if not bot_manager:
        raise HTTPException(status_code=503, detail="Bot manager not initialized")
    
    try:
        balance = await bot_manager.solana_client.get_balance(bot_manager.solana_client.wallet_address)
        return {
            "address": bot_manager.solana_client.wallet_address,
            "balance": balance
        }
    except Exception as e:
        logger.error(f"Failed to get bot balance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get bot balance: {str(e)}")
