"""
Configuration settings for the Solana Copy Trading Bot.
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # Solana RPC Configuration
    solana_rpc_url: str = Field(
        default="https://api.mainnet-beta.solana.com",
        description="Solana RPC endpoint URL"
    )
    solana_ws_url: str = Field(
        default="wss://api.mainnet-beta.solana.com",
        description="Solana WebSocket endpoint URL"
    )
    
    # Bot Configuration
    bot_wallet_address: str = Field(
        default="",
        description="Your wallet address for copy trading"
    )
    bot_private_key: str = Field(
        default="",
        description="Your wallet private key (base58 encoded)"
    )
    
    # Monitoring Configuration
    target_wallets: str = Field(
        default="",
        description="Comma-separated list of wallet addresses to monitor"
    )
    max_concurrent_wallets: int = Field(
        default=10,
        description="Maximum number of wallets to monitor simultaneously"
    )
    
    # Trading Configuration
    copy_sol_transfers: bool = Field(
        default=True,
        description="Enable copying SOL transfers"
    )
    copy_spl_transfers: bool = Field(
        default=True,
        description="Enable copying SPL token transfers"
    )
    copy_raydium_swaps: bool = Field(
        default=True,
        description="Enable copying Raydium swaps"
    )
    
    # Risk Management
    max_transaction_amount: float = Field(
        default=1.0,
        description="Maximum SOL amount to copy in a single transaction"
    )
    min_transaction_amount: float = Field(
        default=0.001,
        description="Minimum SOL amount to copy in a single transaction"
    )
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8080, description="API port")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()
