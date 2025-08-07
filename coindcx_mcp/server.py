import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .client import CoinDCXClient


load_dotenv()

# Configure logging to stderr so it doesn't interfere with MCP protocol
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

app = Server("coindcx-mcp")

# Log server startup
logger.info("CoinDCX MCP Server starting up...")

# Global client instance
client: Optional[CoinDCXClient] = None


def get_client() -> CoinDCXClient:
    """Get or create CoinDCX client instance."""
    global client
    if client is None:
        api_key = os.getenv("COINDCX_API_KEY", "")
        secret_key = os.getenv("COINDCX_SECRET_KEY", "")
        base_url = os.getenv("COINDCX_BASE_URL", "https://api.coindcx.com")
        
        if not api_key or not secret_key:
            raise ValueError("CoinDCX API credentials not found. Please set COINDCX_API_KEY and COINDCX_SECRET_KEY environment variables.")
        
        client = CoinDCXClient(api_key, secret_key, base_url)
    
    return client


@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="get_ticker",
            description="Get ticker data for all markets on CoinDCX",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            }
        ),
        types.Tool(
            name="get_markets",
            description="Get all available trading markets on CoinDCX",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            }
        ),
        types.Tool(
            name="get_market_details",
            description="Get detailed information about a specific trading pair",
            inputSchema={
                "type": "object",
                "properties": {
                    "pair": {
                        "type": "string",
                        "description": "Trading pair symbol (e.g., 'B-BTC_USDT')"
                    }
                },
                "required": ["pair"],
                "additionalProperties": False,
            }
        ),
        types.Tool(
            name="get_trades",
            description="Get recent trades for a specific market",
            inputSchema={
                "type": "object",
                "properties": {
                    "pair": {
                        "type": "string",
                        "description": "Trading pair symbol (e.g., 'B-BTC_USDT')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of trades to retrieve (default: 30, max: 5000)",
                        "minimum": 1,
                        "maximum": 5000
                    }
                },
                "required": ["pair"],
                "additionalProperties": False,
            }
        ),
        types.Tool(
            name="get_order_book",
            description="Get order book (bids and asks) for a specific market",
            inputSchema={
                "type": "object",
                "properties": {
                    "pair": {
                        "type": "string",
                        "description": "Trading pair symbol (e.g., 'B-BTC_USDT')"
                    }
                },
                "required": ["pair"],
                "additionalProperties": False,
            }
        ),
        types.Tool(
            name="get_candles",
            description="Get candlestick/OHLCV data for a specific market. If start_time/end_time are not available or invalid, returns most recent candles.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pair": {
                        "type": "string",
                        "description": "Trading pair symbol (e.g., 'BTCUSDT')"
                    },
                    "interval": {
                        "type": "string",
                        "description": "Candle interval (1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 1d, 3d, 1w, 1M)",
                        "enum": ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "1d", "3d", "1w", "1M"]
                    },
                    "start_time": {
                        "type": "integer",
                        "description": "Start timestamp in milliseconds (optional - if not provided or invalid, returns recent data)"
                    },
                    "end_time": {
                        "type": "integer",
                        "description": "End timestamp in milliseconds (optional - if not provided or invalid, returns recent data)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of candles to retrieve (default: 100, max: 1000)",
                        "minimum": 1,
                        "maximum": 1000
                    }
                },
                "required": ["pair", "interval"],
                "additionalProperties": False,
            }
        ),
        types.Tool(
            name="get_balances",
            description="Get account balances for all assets",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            }
        ),
        types.Tool(
            name="get_user_info",
            description="Get user account information",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            }
        ),
        types.Tool(
            name="create_order",
            description="Create a new buy or sell order",
            inputSchema={
                "type": "object",
                "properties": {
                    "side": {
                        "type": "string",
                        "description": "Order side",
                        "enum": ["buy", "sell"]
                    },
                    "order_type": {
                        "type": "string",
                        "description": "Order type",
                        "enum": ["market_order", "limit_order", "stop_order"]
                    },
                    "market": {
                        "type": "string",
                        "description": "Trading pair (e.g., 'BTCUSDT')"
                    },
                    "price": {
                        "type": "number",
                        "description": "Price per unit (required for limit orders)"
                    },
                    "quantity": {
                        "type": "number",
                        "description": "Quantity to buy/sell"
                    },
                    "total_quantity": {
                        "type": "number",
                        "description": "Total quantity (for market orders)"
                    },
                    "client_order_id": {
                        "type": "string",
                        "description": "Custom order ID for tracking"
                    }
                },
                "required": ["side", "order_type", "market"],
                "additionalProperties": False,
            }
        ),
        types.Tool(
            name="get_order_status",
            description="Get status of a specific order",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID to check status for"
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False,
            }
        ),
        types.Tool(
            name="cancel_order",
            description="Cancel an existing order",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID to cancel"
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False,
            }
        ),
        types.Tool(
            name="get_active_orders",
            description="Get all active orders",
            inputSchema={
                "type": "object",
                "properties": {
                    "market": {
                        "type": "string",
                        "description": "Filter by trading pair (optional)"
                    },
                    "side": {
                        "type": "string",
                        "description": "Filter by order side (optional)",
                        "enum": ["buy", "sell"]
                    }
                },
                "additionalProperties": False,
            }
        ),
        types.Tool(
            name="get_order_history",
            description="Get historical orders",
            inputSchema={
                "type": "object",
                "properties": {
                    "market": {
                        "type": "string",
                        "description": "Filter by trading pair (optional)"
                    },
                    "side": {
                        "type": "string",
                        "description": "Filter by order side (optional)",
                        "enum": ["buy", "sell"]
                    },
                    "from_timestamp": {
                        "type": "integer",
                        "description": "Start timestamp in milliseconds (optional)"
                    },
                    "to_timestamp": {
                        "type": "integer",
                        "description": "End timestamp in milliseconds (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of orders to retrieve (default: 500, max: 1000)",
                        "minimum": 1,
                        "maximum": 1000
                    }
                },
                "additionalProperties": False,
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls."""
    logger.info(f"Calling tool: {name} with arguments: {arguments}")
    try:
        client = get_client()
        result = None
        
        if name == "get_ticker":
            result = client.get_ticker()
        elif name == "get_markets":
            result = client.get_markets()
        elif name == "get_market_details":
            result = client.get_market_details(arguments["pair"])
        elif name == "get_trades":
            limit = arguments.get("limit", 30)
            result = client.get_trades(arguments["pair"], limit)
        elif name == "get_order_book":
            result = client.get_order_book(arguments["pair"])
        elif name == "get_candles":
            limit = arguments.get("limit", 100)
            # Provide default time range if not specified
            current_time = int(__import__('time').time() * 1000)
            default_start_time = current_time - (24 * 60 * 60 * 1000)  # 24 hours ago
            default_end_time = current_time
            
            start_time = arguments.get("start_time", default_start_time)
            end_time = arguments.get("end_time", default_end_time)
            
            result = client.get_candles(
                arguments["pair"],
                arguments["interval"],
                start_time,
                end_time,
                limit
            )
        elif name == "get_balances":
            result = client.get_balances()
        elif name == "get_user_info":
            result = client.get_user_info()
        elif name == "create_order":
            result = client.create_order(
                arguments["side"],
                arguments["order_type"],
                arguments["market"],
                arguments.get("price"),
                arguments.get("quantity"),
                arguments.get("total_quantity"),
                arguments.get("client_order_id")
            )
        elif name == "get_order_status":
            result = client.get_order_status(arguments["order_id"])
        elif name == "cancel_order":
            result = client.cancel_order(arguments["order_id"])
        elif name == "get_active_orders":
            result = client.get_active_orders(
                arguments.get("market"),
                arguments.get("side")
            )
        elif name == "get_order_history":
            result = client.get_order_history(
                arguments.get("market"),
                arguments.get("side"),
                arguments.get("from_timestamp"),
                arguments.get("to_timestamp"),
                arguments.get("limit", 500)
            )
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    except Exception as e:
        error_msg = f"Error calling {name}: {str(e)}"
        return [types.TextContent(type="text", text=error_msg)]


async def main():
    """Main entry point for the server."""
    logger.info("Starting MCP server with stdio transport...")
    async with stdio_server() as streams:
        logger.info("Server is running and ready to accept connections")
        await app.run(streams[0], streams[1], app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())