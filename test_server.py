#!/usr/bin/env python3
"""Test script for CoinDCX MCP server."""

import asyncio
import json
import sys
from coindcx_mcp.server import app


async def test_server():
    """Test the MCP server functionality."""
    print("Testing CoinDCX MCP Server...")
    
    try:
        # Test listing tools
        print("\n1. Testing tool listing...")
        from coindcx_mcp.server import list_tools
        tools = list_tools()
        print(f"Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Test public endpoints (no auth required)
        print("\n2. Testing public endpoints...")
        
        # Test get_ticker
        try:
            from coindcx_mcp.server import call_tool
            result = call_tool("get_ticker", {})
            print("✓ get_ticker: Success")
        except Exception as e:
            print(f"✗ get_ticker: {str(e)}")
        
        # Test get_markets
        try:
            result = call_tool("get_markets", {})
            print("✓ get_markets: Success")
        except Exception as e:
            print(f"✗ get_markets: {str(e)}")
        
        print("\n3. Testing authenticated endpoints...")
        print("Note: These will fail without valid API credentials in .env file")
        
        # Test get_balances (requires auth)
        try:
            result = call_tool("get_balances", {})
            if "Error" in str(result):
                print("✗ get_balances: Authentication required")
            else:
                print("✓ get_balances: Success")
        except Exception as e:
            print(f"✗ get_balances: {str(e)}")
        
        print("\nServer test completed!")
        print("\nTo use with Claude Desktop, add this configuration:")
        print(json.dumps({
            "mcpServers": {
                "coindcx": {
                    "command": "python",
                    "args": ["-m", "coindcx_mcp.server"],
                    "cwd": "/Users/biswajit.kumar/coindcx-mcp"
                }
            }
        }, indent=2))
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)