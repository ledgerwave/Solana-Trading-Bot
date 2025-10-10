#!/usr/bin/env python3
"""
Setup script to create .env file for the Solana Copy Trading Bot.
"""

import os
import shutil

def create_env_file():
    """Create .env file from template."""
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled.")
            return
    
    # Copy from template
    if os.path.exists('env_config.txt'):
        shutil.copy('env_config.txt', '.env')
        print("✅ Created .env file from template")
    else:
        # Create .env file directly
        env_content = """# Solana Copy Trading Bot Environment Configuration

# Solana RPC Configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_WS_URL=wss://api.mainnet-beta.solana.com

# Bot Wallet Configuration
BOT_WALLET_ADDRESS=CyfmfVzK3a4415q9qKfvwem3nyQ6EoQsbykjB2pUmpoz
BOT_PRIVATE_KEY=2x2cyLvtqU1RkDDCBHiRRrbX6DgQ5Cqzyj4eLwZQ8T57kokC82pVw7ZgHWD5V6UdVgcQpQVBM31DA8EXWMivmgak

# Target Wallets to Monitor (comma-separated)
TARGET_WALLETS=

# Trading Configuration
COPY_SOL_TRANSFERS=true
COPY_SPL_TRANSFERS=true
COPY_RAYDIUM_SWAPS=true

# Risk Management
MAX_TRANSACTION_AMOUNT=1.0
MIN_TRANSACTION_AMOUNT=0.001

# API Configuration
API_HOST=0.0.0.0
API_PORT=8080
DEBUG=false

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with default configuration")
    
    print("\n📝 Your .env file has been created with the following settings:")
    print("   • API Port: 8080")
    print("   • Your Wallet: CyfmfVzK3a4415q9qKfvwem3nyQ6EoQsbykjB2pUmpoz")
    print("   • Max Transaction: 1.0 SOL")
    print("   • Min Transaction: 0.001 SOL")
    print("\n🔧 You can edit .env to customize your configuration")
    print("🚀 Run 'python start_bot.py' to start the bot")

if __name__ == "__main__":
    print("🔧 Setting up Solana Copy Trading Bot environment...")
    create_env_file()
