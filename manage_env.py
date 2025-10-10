#!/usr/bin/env python3
"""
Environment management script for the Solana Copy Trading Bot.
"""

import os
import sys
from pathlib import Path

def show_env_status():
    """Show current environment configuration."""
    print("🔧 Current .env Configuration:")
    print("-" * 40)
    
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if 'PRIVATE_KEY' in key:
                        print(f"  {key}: {'*' * 20} (hidden)")
                    else:
                        print(f"  {key}: {value}")
    else:
        print("  ❌ No .env file found")
        print("  💡 Run 'python setup_env.py' to create one")

def edit_env():
    """Edit the .env file."""
    if not os.path.exists('.env'):
        print("❌ No .env file found. Run 'python setup_env.py' first.")
        return
    
    print("📝 Opening .env file for editing...")
    print("💡 Common settings to modify:")
    print("   • TARGET_WALLETS: Add wallet addresses to monitor (comma-separated)")
    print("   • MAX_TRANSACTION_AMOUNT: Maximum SOL to copy")
    print("   • MIN_TRANSACTION_AMOUNT: Minimum SOL to copy")
    print("   • API_PORT: Change the API port (default: 8080)")
    print()
    
    # Try to open with common editors
    editors = ['nano', 'vim', 'code', 'gedit']
    for editor in editors:
        if os.system(f"which {editor} > /dev/null 2>&1") == 0:
            os.system(f"{editor} .env")
            return
    
    print("⚠️  No suitable editor found. Please edit .env manually.")

def add_wallet():
    """Add a wallet to monitor."""
    if not os.path.exists('.env'):
        print("❌ No .env file found. Run 'python setup_env.py' first.")
        return
    
    wallet = input("Enter wallet address to monitor: ").strip()
    if not wallet:
        print("❌ No wallet address provided")
        return
    
    # Read current .env
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    # Update TARGET_WALLETS
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('TARGET_WALLETS='):
            current = line.split('=', 1)[1].strip()
            if current:
                lines[i] = f"TARGET_WALLETS={current},{wallet}\n"
            else:
                lines[i] = f"TARGET_WALLETS={wallet}\n"
            updated = True
            break
    
    if not updated:
        lines.append(f"TARGET_WALLETS={wallet}\n")
    
    # Write back
    with open('.env', 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Added wallet {wallet} to monitoring list")

def main():
    """Main menu."""
    while True:
        print("\n🔧 Solana Copy Trading Bot - Environment Manager")
        print("=" * 50)
        print("1. Show current configuration")
        print("2. Edit .env file")
        print("3. Add wallet to monitor")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            show_env_status()
        elif choice == '2':
            edit_env()
        elif choice == '3':
            add_wallet()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()
