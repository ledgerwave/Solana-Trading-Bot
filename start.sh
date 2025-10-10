#!/bin/bash

# Solana Copy Trading Bot Startup Script

echo "Starting Solana Copy Trading Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the bot
echo "Starting the bot..."
python run.py
