# Solana Copy Trading Bot - Usage Guide

## 🚀 Quick Start

### 1. Start the Bot
```bash
cd /root/dev/solana-trading-bot
source venv/bin/activate
python start_bot.py
```

### 2. Access the API
- **API Base URL**: http://localhost:8080
- **Interactive Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health  

## 📊 API Endpoints

### Bot Control
```bash
# Check bot status
curl http://localhost:8080/api/v1/status

# Start the bot
curl -X POST http://localhost:8080/api/v1/start

# Stop the bot
curl -X POST http://localhost:8080/api/v1/stop
```

### Wallet Management
```bash
# List monitored wallets
curl http://localhost:8080/api/v1/wallets

# Add a wallet to monitor
curl -X POST http://localhost:8080/api/v1/wallets \
  -H "Content-Type: application/json" \
  -d '{
    "address": "wallet_address_here",
    "enabled": true,
    "copy_sol": true,
    "copy_spl": true,
    "copy_swaps": true,
    "max_amount": 1.0
  }'

# Remove a wallet
curl -X DELETE http://localhost:8080/api/v1/wallets/wallet_address_here
```

### Monitoring & Statistics
```bash
# Get transaction history
curl http://localhost:8080/api/v1/transactions?limit=50

# Get trading statistics
curl http://localhost:8080/api/v1/stats

# Check your wallet balance
curl http://localhost:8080/api/v1/bot/balance
```

## 🔧 Configuration

Your bot uses a `.env` file for configuration. The bot is pre-configured with:
- **Your Wallet**: `CyfmfVzK3a4415q9qKfvwem3nyQ6EoQsbykjB2pUmpoz`
- **Max Transaction**: 1.0 SOL
- **Min Transaction**: 0.001 SOL
- **API Port**: 8080

### Environment Configuration

The bot loads configuration from `.env` file. You can:

1. **View current config**: `python manage_env.py`
2. **Edit configuration**: Edit `.env` file directly
3. **Add wallets**: Use the management script or edit `.env`

### Key Environment Variables

```env
# Your wallet configuration
BOT_WALLET_ADDRESS=your_wallet_address
BOT_PRIVATE_KEY=your_private_key

# Wallets to monitor (comma-separated)
TARGET_WALLETS=wallet1,wallet2,wallet3

# Trading limits
MAX_TRANSACTION_AMOUNT=1.0
MIN_TRANSACTION_AMOUNT=0.001

# API settings
API_PORT=8080
```

## 📈 How to Use

1. **Start the Bot**: Run `python start_bot.py`
2. **Add Target Wallets**: Use the API to add wallets you want to monitor
3. **Configure Limits**: Set appropriate transaction amount limits
4. **Monitor Activity**: Use the API endpoints to track performance
5. **View Logs**: Check the console output for real-time activity

## 🛡️ Security Notes

- Your private key is configured in the environment
- Test with small amounts first
- Monitor the bot's performance regularly
- Keep your private key secure

## 🔍 Example Workflow

1. Start the bot: `python start_bot.py`
2. Add a wallet to monitor:
   ```bash
   curl -X POST http://localhost:8080/api/v1/wallets \
     -H "Content-Type: application/json" \
     -d '{"address": "target_wallet_address", "enabled": true}'
   ```
3. Start monitoring: `curl -X POST http://localhost:8080/api/v1/start`
4. Check status: `curl http://localhost:8080/api/v1/status`
5. View transactions: `curl http://localhost:8080/api/v1/transactions`

## 🚨 Important Notes

- The bot is ready for production use
- All dependencies are installed and working
- Your wallet is pre-configured
- The bot supports SOL transfers, SPL token transfers, and Raydium swaps
- Comprehensive error handling and logging is included
