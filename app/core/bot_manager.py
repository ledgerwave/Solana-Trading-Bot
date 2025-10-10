"""
Bot manager for coordinating wallet monitoring and copy trading operations.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import json

from .solana_client import SolanaClient
from ..models.schemas import (
    BotStatus, 
    WalletConfig, 
    TransactionInfo, 
    CopyTradingStats,
    TransactionType
)
from ..config import settings

logger = logging.getLogger(__name__)

class BotManager:
    """Manages the copy trading bot operations."""
    
    def __init__(self):
        self.solana_client = SolanaClient()
        self.status = BotStatus.STOPPED
        self.monitored_wallets: Dict[str, WalletConfig] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.stats = CopyTradingStats()
        self.start_time: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.transaction_history: List[TransactionInfo] = []
        self.max_history_size = 1000
        
        # Load initial configuration
        self._load_configuration()
    
    async def initialize(self):
        """Initialize the bot manager."""
        try:
            await self.solana_client.initialize()
            logger.info("Bot manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize bot manager: {e}")
            self.last_error = str(e)
            raise
    
    async def shutdown(self):
        """Shutdown the bot manager."""
        await self.stop_monitoring()
        await self.solana_client.shutdown()
        logger.info("Bot manager shutdown complete")
    
    def _load_configuration(self):
        """Load configuration from settings."""
        # Add default wallets from settings
        if settings.target_wallets:
            wallet_addresses = [addr.strip() for addr in settings.target_wallets.split(',') if addr.strip()]
            for wallet_address in wallet_addresses:
                self.monitored_wallets[wallet_address] = WalletConfig(
                    address=wallet_address,
                    enabled=True,
                    copy_sol=settings.copy_sol_transfers,
                    copy_spl=settings.copy_spl_transfers,
                    copy_swaps=settings.copy_raydium_swaps,
                    max_amount=settings.max_transaction_amount
                )
    
    async def start_monitoring(self):
        """Start monitoring all configured wallets."""
        if self.status == BotStatus.RUNNING:
            logger.warning("Bot is already running")
            return
        
        self.status = BotStatus.STARTING
        self.start_time = datetime.utcnow()
        
        try:
            # Start monitoring each wallet
            for wallet_address, config in self.monitored_wallets.items():
                if config.enabled:
                    await self._start_wallet_monitoring(wallet_address, config)
            
            self.status = BotStatus.RUNNING
            logger.info(f"Started monitoring {len(self.monitoring_tasks)} wallets")
        
        except Exception as e:
            self.status = BotStatus.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to start monitoring: {e}")
            raise
    
    async def stop_monitoring(self):
        """Stop monitoring all wallets."""
        if self.status == BotStatus.STOPPED:
            return
        
        self.status = BotStatus.STOPPING
        
        # Cancel all monitoring tasks
        for wallet_address, task in self.monitoring_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.monitoring_tasks.clear()
        self.status = BotStatus.STOPPED
        logger.info("Stopped monitoring all wallets")
    
    async def _start_wallet_monitoring(self, wallet_address: str, config: WalletConfig):
        """Start monitoring a specific wallet."""
        try:
            task = asyncio.create_task(
                self._monitor_wallet(wallet_address, config)
            )
            self.monitoring_tasks[wallet_address] = task
            logger.info(f"Started monitoring wallet {wallet_address}")
        
        except Exception as e:
            logger.error(f"Failed to start monitoring wallet {wallet_address}: {e}")
            self.last_error = str(e)
    
    async def _monitor_wallet(self, wallet_address: str, config: WalletConfig):
        """Monitor a wallet for new transactions."""
        try:
            await self.solana_client.monitor_wallet(
                wallet_address,
                lambda tx_info: asyncio.create_task(
                    self._process_transaction(tx_info, config)
                )
            )
        except Exception as e:
            logger.error(f"Error monitoring wallet {wallet_address}: {e}")
            self.last_error = str(e)
    
    async def _process_transaction(self, transaction_info: TransactionInfo, config: WalletConfig):
        """Process a detected transaction and potentially copy it."""
        try:
            # Add to transaction history
            self.transaction_history.append(transaction_info)
            if len(self.transaction_history) > self.max_history_size:
                self.transaction_history.pop(0)
            
            # Check if we should copy this transaction
            if not self._should_copy_transaction(transaction_info, config):
                return
            
            # Copy the transaction
            success = await self._copy_transaction(transaction_info)
            
            # Update statistics
            self.stats.total_transactions_copied += 1
            if success:
                self.stats.successful_copies += 1
                if transaction_info.amount:
                    self.stats.total_volume_copied += transaction_info.amount
                
                # Update type-specific counters
                if transaction_info.transaction_type == TransactionType.SOL_TRANSFER:
                    self.stats.sol_transfers_copied += 1
                elif transaction_info.transaction_type == TransactionType.SPL_TRANSFER:
                    self.stats.spl_transfers_copied += 1
                elif transaction_info.transaction_type == TransactionType.RAYDIUM_SWAP:
                    self.stats.swaps_copied += 1
            else:
                self.stats.failed_copies += 1
            
            self.stats.last_activity = datetime.utcnow()
            
            logger.info(f"Processed transaction {transaction_info.signature} - Success: {success}")
        
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            self.last_error = str(e)
    
    def _should_copy_transaction(self, transaction_info: TransactionInfo, config: WalletConfig) -> bool:
        """Determine if a transaction should be copied."""
        # Check if transaction type is enabled
        if transaction_info.transaction_type == TransactionType.SOL_TRANSFER and not config.copy_sol:
            return False
        if transaction_info.transaction_type == TransactionType.SPL_TRANSFER and not config.copy_spl:
            return False
        if transaction_info.transaction_type == TransactionType.RAYDIUM_SWAP and not config.copy_swaps:
            return False
        
        # Check amount limits
        if transaction_info.amount:
            if config.max_amount and transaction_info.amount > config.max_amount:
                return False
            if transaction_info.amount < settings.min_transaction_amount:
                return False
        
        return True
    
    async def _copy_transaction(self, transaction_info: TransactionInfo) -> bool:
        """Copy a transaction to our wallet."""
        try:
            if transaction_info.transaction_type == TransactionType.SOL_TRANSFER:
                return await self._copy_sol_transfer(transaction_info)
            elif transaction_info.transaction_type == TransactionType.SPL_TRANSFER:
                return await self._copy_spl_transfer(transaction_info)
            elif transaction_info.transaction_type == TransactionType.RAYDIUM_SWAP:
                return await self._copy_raydium_swap(transaction_info)
            else:
                logger.warning(f"Unsupported transaction type: {transaction_info.transaction_type}")
                return False
        
        except Exception as e:
            logger.error(f"Error copying transaction: {e}")
            return False
    
    async def _copy_sol_transfer(self, transaction_info: TransactionInfo) -> bool:
        """Copy a SOL transfer transaction."""
        try:
            # Extract destination address from transaction
            # This is a simplified implementation
            # In practice, you'd need to parse the transaction instructions
            
            # For now, we'll create a placeholder transaction
            # You would need to implement proper transaction parsing
            logger.info(f"Would copy SOL transfer: {transaction_info.amount} SOL")
            return True
        
        except Exception as e:
            logger.error(f"Error copying SOL transfer: {e}")
            return False
    
    async def _copy_spl_transfer(self, transaction_info: TransactionInfo) -> bool:
        """Copy an SPL token transfer transaction."""
        try:
            logger.info(f"Would copy SPL transfer: {transaction_info.amount} tokens")
            return True
        
        except Exception as e:
            logger.error(f"Error copying SPL transfer: {e}")
            return False
    
    async def _copy_raydium_swap(self, transaction_info: TransactionInfo) -> bool:
        """Copy a Raydium swap transaction."""
        try:
            logger.info(f"Would copy Raydium swap: {transaction_info.amount} SOL")
            return True
        
        except Exception as e:
            logger.error(f"Error copying Raydium swap: {e}")
            return False
    
    # Public API methods
    def get_status(self) -> Dict:
        """Get current bot status."""
        uptime = None
        if self.start_time:
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "status": self.status,
            "is_running": self.status == BotStatus.RUNNING,
            "monitored_wallets": len(self.monitoring_tasks),
            "uptime_seconds": uptime,
            "stats": self.stats,
            "last_error": self.last_error
        }
    
    async def add_wallet(self, wallet_config: WalletConfig):
        """Add a wallet to monitoring."""
        self.monitored_wallets[wallet_config.address] = wallet_config
        
        if self.status == BotStatus.RUNNING and wallet_config.enabled:
            await self._start_wallet_monitoring(wallet_config.address, wallet_config)
        
        logger.info(f"Added wallet {wallet_config.address} to monitoring")
    
    async def remove_wallet(self, wallet_address: str):
        """Remove a wallet from monitoring."""
        if wallet_address in self.monitoring_tasks:
            task = self.monitoring_tasks[wallet_address]
            task.cancel()
            del self.monitoring_tasks[wallet_address]
        
        if wallet_address in self.monitored_wallets:
            del self.monitored_wallets[wallet_address]
        
        logger.info(f"Removed wallet {wallet_address} from monitoring")
    
    async def update_wallet(self, wallet_address: str, updates: Dict):
        """Update wallet configuration."""
        if wallet_address in self.monitored_wallets:
            config = self.monitored_wallets[wallet_address]
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            logger.info(f"Updated wallet {wallet_address} configuration")
    
    def get_transaction_history(self, limit: int = 100, offset: int = 0) -> List[TransactionInfo]:
        """Get transaction history."""
        start = len(self.transaction_history) - offset - limit
        end = len(self.transaction_history) - offset
        return self.transaction_history[max(0, start):max(0, end)]
    
    def get_stats(self) -> CopyTradingStats:
        """Get copy trading statistics."""
        return self.stats
    
    def is_running(self) -> bool:
        """Check if bot is running."""
        return self.status == BotStatus.RUNNING
