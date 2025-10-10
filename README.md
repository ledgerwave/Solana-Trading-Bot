# Solana Copy Trading Bot

A real-time Solana wallet monitoring and copy trading bot built with Python and FastAPI.

## Features

- **Real-time Monitoring**: Monitors multiple Solana wallets simultaneously using WebSocket connections
- **Transaction Detection**: Uses `logsSubscribe` to detect new transactions in real-time
- **Copy Trading**: Automatically copies SOL transfers, SPL token transfers, and program interactions
- **Parallel Processing**: Monitors all wallets concurrently using asyncio
- **Error Handling**: Robust error handling with automatic reconnection
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **REST API**: FastAPI-based API for bot management and monitoring

## How It Works

1. **Wallet Monitoring**: The bot connects to Solana mainnet via WebSocket and subscribes to logs for each target wallet
2. **Transaction Detection**: When a new transaction is detected, the bot fetches full transaction details using `getTransaction`
3. **Transaction Analysis**: The bot parses the transaction to determine if it's a SOL transfer, SPL token transfer, or program interaction
4. **Copy Execution**: For supported transaction types, the bot reconstructs an equivalent transaction for your wallet and sends it immediately

## Supported Transaction Types

- **SOL Transfers**: Basic SOL transfers between wallets
- **SPL Token Transfers**: Token transfers using the SPL Token Program
- **Raydium Swaps**: Automated market maker swaps (placeholder implementation)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd solana-trading-bot
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Configuration

Edit the `.env` file with your configuration:

```env
# Your wallet configuration
BOT_WALLET_ADDRESS=your_wallet_address
BOT_PRIVATE_KEY=your_private_key

# Wallets to monitor
TARGET_WALLETS=wallet1,wallet2,wallet3

# Trading settings
COPY_SOL_TRANSFERS=true
COPY_SPL_TRANSFERS=true
COPY_RAYDIUM_SWAPS=true
MAX_TRANSACTION_AMOUNT=1.0
MIN_TRANSACTION_AMOUNT=0.001
```

## Usage

### Starting the Bot

```bash
# Development mode
python -m app.main

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

The bot provides a REST API for management:

- `GET /` - Basic information
- `GET /health` - Health check
- `GET /api/v1/status` - Bot status and statistics
- `POST /api/v1/start` - Start the bot
- `POST /api/v1/stop` - Stop the bot
- `GET /api/v1/wallets` - List monitored wallets
- `POST /api/v1/wallets` - Add a wallet to monitor
- `PUT /api/v1/wallets/{address}` - Update wallet configuration
- `DELETE /api/v1/wallets/{address}` - Remove wallet from monitoring
- `GET /api/v1/transactions` - Get transaction history
- `GET /api/v1/stats` - Get trading statistics
- `GET /api/v1/bot/balance` - Get bot wallet balance

### Example API Usage

```bash
# Start the bot
curl -X POST http://localhost:8000/api/v1/start

# Check status
curl http://localhost:8000/api/v1/status

# Add a wallet to monitor
curl -X POST http://localhost:8000/api/v1/wallets \
  -H "Content-Type: application/json" \
  -d '{"address": "wallet_address", "enabled": true}'

# Get transaction history
curl http://localhost:8000/api/v1/transactions?limit=50
```

## Project Structure

```
solana-trading-bot/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── solana_client.py    # Solana blockchain client
│   │   └── bot_manager.py      # Bot management logic
│   └── api/
│       ├── __init__.py
│       └── endpoints.py        # API endpoints
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
└── README.md                  # This file
```

## Security Considerations

⚠️ **IMPORTANT**: This bot handles private keys and real money. Please consider:

1. **Private Key Security**: Store private keys securely and never commit them to version control
2. **Testnet First**: Test thoroughly on Solana testnet before using on mainnet
3. **Amount Limits**: Set appropriate limits to prevent large losses
4. **Monitoring**: Monitor the bot's performance and logs regularly
5. **Backup**: Keep backups of your wallet and configuration

## Development

### Running Tests

```bash
pytest
```

### Code Style

The project follows Python best practices with type hints and async/await patterns.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes. Use at your own risk.

## Disclaimer

This software is provided "as is" without warranty. Trading cryptocurrencies involves risk, and you should never invest more than you can afford to lose. The authors are not responsible for any financial losses.
