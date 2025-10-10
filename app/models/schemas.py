"""
Pydantic schemas for API request/response models.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    """Transaction type enumeration."""
    SOL_TRANSFER = "sol_transfer"
    SPL_TRANSFER = "spl_transfer"
    RAYDIUM_SWAP = "raydium_swap"
    PROGRAM_INTERACTION = "program_interaction"
    UNKNOWN = "unknown"

class BotStatus(str, Enum):
    """Bot status enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"

class WalletConfig(BaseModel):
    """Wallet configuration model."""
    address: str = Field(..., description="Wallet address to monitor")
    enabled: bool = Field(default=True, description="Whether monitoring is enabled")
    copy_sol: bool = Field(default=True, description="Copy SOL transfers")
    copy_spl: bool = Field(default=True, description="Copy SPL transfers")
    copy_swaps: bool = Field(default=True, description="Copy swaps")
    max_amount: Optional[float] = Field(default=None, description="Maximum amount to copy")

class BotConfig(BaseModel):
    """Bot configuration model."""
    target_wallets: List[WalletConfig] = Field(default=[], description="Wallets to monitor")
    copy_sol_transfers: bool = Field(default=True, description="Enable SOL transfer copying")
    copy_spl_transfers: bool = Field(default=True, description="Enable SPL transfer copying")
    copy_raydium_swaps: bool = Field(default=True, description="Enable Raydium swap copying")
    max_transaction_amount: float = Field(default=1.0, description="Maximum transaction amount")
    min_transaction_amount: float = Field(default=0.001, description="Minimum transaction amount")

class TransactionInfo(BaseModel):
    """Transaction information model."""
    signature: str = Field(..., description="Transaction signature")
    block_time: Optional[datetime] = Field(None, description="Block timestamp")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    source_wallet: str = Field(..., description="Source wallet address")
    amount: Optional[float] = Field(None, description="Transaction amount in SOL")
    token_mint: Optional[str] = Field(None, description="Token mint address for SPL transfers")
    success: bool = Field(..., description="Whether transaction was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    raw_data: Dict[str, Any] = Field(default={}, description="Raw transaction data")

class CopyTradingStats(BaseModel):
    """Copy trading statistics model."""
    total_transactions_copied: int = Field(default=0, description="Total transactions copied")
    successful_copies: int = Field(default=0, description="Successful copy transactions")
    failed_copies: int = Field(default=0, description="Failed copy transactions")
    total_volume_copied: float = Field(default=0.0, description="Total volume copied in SOL")
    sol_transfers_copied: int = Field(default=0, description="SOL transfers copied")
    spl_transfers_copied: int = Field(default=0, description="SPL transfers copied")
    swaps_copied: int = Field(default=0, description="Swaps copied")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")

class BotStatusResponse(BaseModel):
    """Bot status response model."""
    status: BotStatus = Field(..., description="Current bot status")
    is_running: bool = Field(..., description="Whether bot is running")
    monitored_wallets: int = Field(..., description="Number of monitored wallets")
    uptime_seconds: Optional[float] = Field(None, description="Bot uptime in seconds")
    stats: CopyTradingStats = Field(..., description="Trading statistics")
    last_error: Optional[str] = Field(None, description="Last error message")

class AddWalletRequest(BaseModel):
    """Request model for adding a wallet."""
    address: str = Field(..., description="Wallet address to monitor")
    enabled: bool = Field(default=True, description="Whether to enable monitoring")
    copy_sol: bool = Field(default=True, description="Copy SOL transfers")
    copy_spl: bool = Field(default=True, description="Copy SPL transfers")
    copy_swaps: bool = Field(default=True, description="Copy swaps")
    max_amount: Optional[float] = Field(default=None, description="Maximum amount to copy")

class UpdateWalletRequest(BaseModel):
    """Request model for updating wallet configuration."""
    enabled: Optional[bool] = Field(None, description="Whether monitoring is enabled")
    copy_sol: Optional[bool] = Field(None, description="Copy SOL transfers")
    copy_spl: Optional[bool] = Field(None, description="Copy SPL transfers")
    copy_swaps: Optional[bool] = Field(None, description="Copy swaps")
    max_amount: Optional[float] = Field(None, description="Maximum amount to copy")

class TransactionHistoryResponse(BaseModel):
    """Response model for transaction history."""
    transactions: List[TransactionInfo] = Field(..., description="List of transactions")
    total_count: int = Field(..., description="Total number of transactions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of transactions per page")

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
