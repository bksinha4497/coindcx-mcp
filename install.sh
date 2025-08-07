#!/bin/bash
# Installation script for CoinDCX MCP Server

echo "🚀 Installing CoinDCX MCP Server..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install -e .

# Copy environment template if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env configuration file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your CoinDCX API credentials"
fi

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your CoinDCX API credentials"
echo "2. Add this server to your Claude Desktop configuration:"
echo ""
echo "macOS: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "Windows: %APPDATA%/Claude/claude_desktop_config.json"
echo ""
echo "Configuration:"
echo '{'
echo '  "mcpServers": {'
echo '    "coindcx": {'
echo '      "command": "python",'
echo '      "args": ["-m", "coindcx_mcp.server"],'
echo "      \"cwd\": \"$(pwd)\""
echo '    }'
echo '  }'
echo '}'
echo ""
echo "3. Restart Claude Desktop"