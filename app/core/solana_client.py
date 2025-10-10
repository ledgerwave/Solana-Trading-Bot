"""
Solana client for interacting with the Solana blockchain.
Handles RPC calls, WebSocket connections, and transaction processing.
"""

import asyncio
import json
import logging
import base58
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException
import aiohttp
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.message import Message
from solders.instruction import Instruction
from solders.system_program import TransferParams, transfer
from solders.sysvar import RENT
from solana.rpc.api import Client
from solana.rpc.websocket_api import connect

from ..config import settings
from ..models.schemas import TransactionInfo, TransactionType

logger = logging.getLogger(__name__)

class SolanaClient:
    """Solana blockchain client for RPC and WebSocket operations."""
    
    def __init__(self):
        self.rpc_url = settings.solana_rpc_url
        self.ws_url = settings.solana_ws_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.subscription_ids: Dict[str, int] = {}
        self.running = False
        
        # Initialize keypair from private key
        try:
            private_key_bytes = base58.b58decode(settings.bot_private_key)
            self.keypair = Keypair.from_bytes(private_key_bytes)
            self.wallet_address = str(self.keypair.pubkey())
            logger.info(f"Initialized wallet: {self.wallet_address}")
        except Exception as e:
            logger.error(f"Failed to initialize keypair: {e}")
            raise
    
    async def initialize(self):
        """Initialize the Solana client."""
        self.session = aiohttp.ClientSession()
        self.running = True
        logger.info("Solana client initialized")
    
    async def shutdown(self):
        """Shutdown the Solana client."""
        self.running = False
        
        # Close WebSocket connections
        for wallet, ws in self.ws_connections.items():
            try:
                await ws.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket for {wallet}: {e}")
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        logger.info("Solana client shutdown complete")
    
    async def _make_rpc_call(self, method: str, params: List[Any] = None) -> Dict[str, Any]:
        """Make an RPC call to Solana."""
        if not self.session:
            raise RuntimeError("Client not initialized")
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or []
        }
        
        try:
            async with self.session.post(
                self.rpc_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                
                if "error" in result:
                    raise Exception(f"RPC error: {result['error']}")
                
                return result.get("result")
        except Exception as e:
            logger.error(f"RPC call failed: {e}")
            raise
    
    async def get_latest_blockhash(self) -> str:
        """Get the latest blockhash."""
        result = await self._make_rpc_call("getLatestBlockhash")
        return result["value"]["blockhash"]
    
    async def get_balance(self, address: str) -> float:
        """Get SOL balance for an address."""
        result = await self._make_rpc_call("getBalance", [address])
        return result["value"] / 1e9  # Convert lamports to SOL
    
    async def get_transaction(self, signature: str) -> Optional[Dict[str, Any]]:
        """Get transaction details by signature."""
        try:
            result = await self._make_rpc_call(
                "getTransaction",
                [
                    signature,
                    {
                        "encoding": "json",
                        "maxSupportedTransactionVersion": 0
                    }
                ]
            )
            return result
        except Exception as e:
            logger.error(f"Failed to get transaction {signature}: {e}")
            return None
    
    async def send_transaction(self, transaction: Transaction) -> Optional[str]:
        """Send a transaction to the network."""
        try:
            # Serialize transaction
            serialized = bytes(transaction)
            encoded = base58.b58encode(serialized).decode('utf-8')
            
            result = await self._make_rpc_call("sendTransaction", [encoded])
            return result
        except Exception as e:
            logger.error(f"Failed to send transaction: {e}")
            return None
    
    async def monitor_wallet(self, wallet_address: str, callback: Callable[[TransactionInfo], None]):
        """Monitor a wallet for new transactions using WebSocket."""
        if wallet_address in self.ws_connections:
            logger.warning(f"Already monitoring wallet {wallet_address}")
            return
        
        try:
            # Connect to WebSocket
            ws = await websockets.connect(self.ws_url)
            self.ws_connections[wallet_address] = ws
            
            # Subscribe to logs for this wallet
            subscribe_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "logsSubscribe",
                "params": [
                    {
                        "mentions": [wallet_address]
                    },
                    {
                        "commitment": "confirmed"
                    }
                ]
            }
            
            await ws.send(json.dumps(subscribe_payload))
            response = await ws.recv()
            response_data = json.loads(response)
            
            if "result" in response_data:
                subscription_id = response_data["result"]
                self.subscription_ids[wallet_address] = subscription_id
                logger.info(f"Subscribed to logs for wallet {wallet_address} (ID: {subscription_id})")
            else:
                logger.error(f"Failed to subscribe to wallet {wallet_address}: {response_data}")
                return
            
            # Listen for new transactions
            while self.running:
                try:
                    message = await ws.recv()
                    data = json.loads(message)
                    
                    if "params" in data and data["params"].get("subscription") == subscription_id:
                        await self._process_log_notification(wallet_address, data["params"]["result"], callback)
                
                except ConnectionClosed:
                    logger.warning(f"WebSocket connection closed for wallet {wallet_address}")
                    break
                except WebSocketException as e:
                    logger.error(f"WebSocket error for wallet {wallet_address}: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error processing message for wallet {wallet_address}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Failed to monitor wallet {wallet_address}: {e}")
        finally:
            # Clean up connection
            if wallet_address in self.ws_connections:
                del self.ws_connections[wallet_address]
            if wallet_address in self.subscription_ids:
                del self.subscription_ids[wallet_address]
    
    async def _process_log_notification(self, wallet_address: str, log_data: Dict[str, Any], callback: Callable[[TransactionInfo], None]):
        """Process a log notification and extract transaction information."""
        try:
            signature = log_data.get("signature")
            if not signature:
                return
            
            # Get full transaction details
            tx_data = await self.get_transaction(signature)
            if not tx_data:
                return
            
            # Parse transaction
            transaction_info = await self._parse_transaction(tx_data, wallet_address)
            if transaction_info:
                await callback(transaction_info)
        
        except Exception as e:
            logger.error(f"Error processing log notification: {e}")
    
    async def _parse_transaction(self, tx_data: Dict[str, Any], source_wallet: str) -> Optional[TransactionInfo]:
        """Parse transaction data and extract relevant information."""
        try:
            meta = tx_data.get("meta", {})
            if meta.get("err"):
                return None  # Skip failed transactions
            
            transaction = tx_data.get("transaction", {})
            message = transaction.get("message", {})
            instructions = message.get("instructions", [])
            
            # Determine transaction type
            transaction_type = TransactionType.UNKNOWN
            amount = None
            token_mint = None
            
            # Check for SOL transfer
            if self._is_sol_transfer(instructions):
                transaction_type = TransactionType.SOL_TRANSFER
                amount = self._extract_sol_amount(instructions, source_wallet)
            
            # Check for SPL token transfer
            elif self._is_spl_transfer(instructions):
                transaction_type = TransactionType.SPL_TRANSFER
                amount, token_mint = self._extract_spl_amount(instructions, source_wallet)
            
            # Check for Raydium swap
            elif self._is_raydium_swap(instructions):
                transaction_type = TransactionType.RAYDIUM_SWAP
                amount = self._extract_swap_amount(instructions, source_wallet)
            
            return TransactionInfo(
                signature=tx_data.get("transaction", {}).get("signatures", [""])[0],
                block_time=datetime.fromtimestamp(tx_data.get("blockTime", 0)) if tx_data.get("blockTime") else None,
                transaction_type=transaction_type,
                source_wallet=source_wallet,
                amount=amount,
                token_mint=token_mint,
                success=True,
                raw_data=tx_data
            )
        
        except Exception as e:
            logger.error(f"Error parsing transaction: {e}")
            return None
    
    def _is_sol_transfer(self, instructions: List[Dict[str, Any]]) -> bool:
        """Check if transaction is a SOL transfer."""
        for instruction in instructions:
            if instruction.get("programIdIndex") == 0:  # System program
                return True
        return False
    
    def _is_spl_transfer(self, instructions: List[Dict[str, Any]]) -> bool:
        """Check if transaction is an SPL token transfer."""
        # This is a simplified check - in practice, you'd need to check program IDs
        return False  # Placeholder implementation
    
    def _is_raydium_swap(self, instructions: List[Dict[str, Any]]) -> bool:
        """Check if transaction is a Raydium swap."""
        # This is a simplified check - in practice, you'd need to check program IDs
        return False  # Placeholder implementation
    
    def _extract_sol_amount(self, instructions: List[Dict[str, Any]], source_wallet: str) -> Optional[float]:
        """Extract SOL amount from transfer instructions."""
        # Simplified implementation - in practice, you'd need to decode instruction data
        return None
    
    def _extract_spl_amount(self, instructions: List[Dict[str, Any]], source_wallet: str) -> tuple[Optional[float], Optional[str]]:
        """Extract SPL token amount and mint from transfer instructions."""
        # Simplified implementation
        return None, None
    
    def _extract_swap_amount(self, instructions: List[Dict[str, Any]], source_wallet: str) -> Optional[float]:
        """Extract swap amount from Raydium instructions."""
        # Simplified implementation
        return None
    
    async def create_sol_transfer(self, to_address: str, amount: float) -> Optional[Transaction]:
        """Create a SOL transfer transaction."""
        try:
            # Get latest blockhash
            blockhash = await self.get_latest_blockhash()
            
            # Create transfer instruction
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=self.keypair.pubkey(),
                    to_pubkey=Pubkey.from_string(to_address),
                    lamports=int(amount * 1e9)  # Convert SOL to lamports
                )
            )
            
            # Create transaction
            message = Message.new_with_blockhash([transfer_ix], self.keypair.pubkey(), blockhash)
            transaction = Transaction([], message, [blockhash])
            
            # Sign transaction
            transaction.sign([self.keypair], blockhash)
            
            return transaction
        
        except Exception as e:
            logger.error(f"Failed to create SOL transfer: {e}")
            return None
    
    async def create_spl_transfer(self, to_address: str, token_mint: str, amount: float) -> Optional[Transaction]:
        """Create an SPL token transfer transaction."""
        # Placeholder implementation
        # In practice, you'd need to:
        # 1. Get token accounts for source and destination
        # 2. Create transfer_checked instruction
        # 3. Build and sign transaction
        return None
