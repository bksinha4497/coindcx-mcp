# CoinDCX MCP Server

A Model Context Protocol (MCP) server that provides CoinDCX cryptocurrency exchange API integration for Claude and other AI assistants.

## Features

- **Public Market Data**: Access ticker, market info, order book, trades, and candlestick data
- **Account Management**: Check balances and user information
- **Trading Operations**: Create, cancel, and monitor orders
- **Order History**: Retrieve active and historical orders
- **Secure Authentication**: HMAC-SHA256 signed requests

## Installation

1. Clone or download this project
2. Install dependencies:
```bash
cd coindcx-mcp
pip install -e .
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your CoinDCX API credentials:
```env
COINDCX_API_KEY=your_api_key_here
COINDCX_SECRET_KEY=your_secret_key_here
COINDCX_BASE_URL=https://api.coindcx.com
```

### Getting API Keys

1. Sign up at [CoinDCX](https://coindcx.com)
2. Go to API Settings in your account
3. Create a new API key with appropriate permissions
4. Copy the API Key and Secret Key to your `.env` file

## Usage with Claude Desktop

Add this server to your Claude Desktop configuration file:

### macOS
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "coindcx": {
      "command": "python",
      "args": ["-m", "coindcx_mcp.server"],
      "cwd": "/path/to/coindcx-mcp"
    }
  }
}
```

### Windows
Edit `%APPDATA%/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "coindcx": {
      "command": "python",
      "args": ["-m", "coindcx_mcp.server"],
      "cwd": "C:\\path\\to\\coindcx-mcp"
    }
  }
}
```

## Available Tools

### Public Market Data
- `get_ticker`: Get ticker data for all markets
- `get_markets`: Get all available trading pairs
- `get_market_details`: Get details for a specific trading pair
- `get_trades`: Get recent trades for a market
- `get_order_book`: Get order book (bids/asks) for a market
- `get_candles`: Get candlestick/OHLCV data

### Account Information
- `get_balances`: Get account balances for all assets
- `get_user_info`: Get user account information

### Trading
- `create_order`: Create buy/sell orders (market, limit, stop)
- `get_order_status`: Check status of a specific order
- `cancel_order`: Cancel an existing order
- `get_active_orders`: Get all active orders
- `get_order_history`: Get historical order data

## Example Queries for Claude

Once configured, you can ask Claude things like:

- "What's the current Bitcoin price on CoinDCX?"
- "Show me my account balances"
- "Create a limit buy order for 0.001 BTC at 45000 USDT"
- "What are my active orders?"
- "Cancel order with ID 12345"
- "Show me the order book for BTCUSDT"

## Security Notes

- Never commit your API keys to version control
- Use environment variables or the `.env` file for credentials
- Consider using API keys with limited permissions for testing
- The server handles authentication automatically using HMAC-SHA256

## Development

To run the server directly:
```bash
python -m coindcx_mcp.server
```

## Troubleshooting

1. **Authentication Errors**: Verify your API key and secret are correct
2. **Permission Errors**: Ensure your API key has the required permissions
3. **Network Errors**: Check your internet connection and CoinDCX API status
4. **Tool Not Found**: Restart Claude Desktop after configuration changes

## API Rate Limits

CoinDCX has rate limits on their API. The server will handle rate limit errors, but be mindful of:
- Order creation: Limited to 2000 requests per 60 seconds
- Other endpoints have varying limits

Refer to [CoinDCX API documentation](https://docs.coindcx.com) for current rate limits.

## Support

For issues with this MCP server, please check:
1. Your API credentials are correct
2. Your network connection is stable
3. CoinDCX API is operational
4. Claude Desktop configuration is properly set up

## License

This project is provided as-is for educational and development purposes.