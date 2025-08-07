import hashlib
import hmac
import json
import time
from typing import Dict, Any, Optional
import httpx
from datetime import datetime


class CoinDCXClient:
    def __init__(self, api_key: str, secret_key: str, base_url: str = "https://api.coindcx.com"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)

    def _generate_signature(self, payload: str, timestamp: int) -> str:
        """Generate HMAC-SHA256 signature for authenticated requests."""
        message = payload + str(timestamp)
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _make_authenticated_request(self, method: str, endpoint: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated request to CoinDCX API."""
        timestamp = int(time.time() * 1000)
        
        if payload is None:
            payload = {}
        
        payload_str = json.dumps(payload, separators=(',', ':'))
        signature = self._generate_signature(payload_str, timestamp)
        
        headers = {
            'Content-Type': 'application/json',
            'X-AUTH-APIKEY': self.api_key,
            'X-AUTH-SIGNATURE': signature
        }
        
        url = f"{self.base_url}{endpoint}"
        
        if method.upper() == 'GET':
            response = self.client.get(url, headers=headers, params=payload)
        else:
            response = self.client.post(url, headers=headers, json=payload)
        
        response.raise_for_status()
        return response.json()

    def _make_public_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make public request to CoinDCX API."""
        url = f"{self.base_url}{endpoint}"
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _make_public_market_data_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make public request to CoinDCX market data API."""
        url = f"https://public.coindcx.com{endpoint}"
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _format_pair_for_public_api(self, pair: str) -> str:
        """Convert pair format from BTCUSDT to B-BTC_USDT for public API."""
        # First, try to find the pair in market details to get the correct format
        try:
            market_details = self.get_market_details(pair)
            if market_details and not market_details.get('error'):
                # Extract the pair format from market details
                api_pair = market_details.get('pair', '')
                if api_pair.startswith('KC-'):
                    # Convert KC-BTC_USDT to B-BTC_USDT
                    return api_pair.replace('KC-', 'B-')
        except:
            pass
        
        # Fallback: manually format common pairs
        if pair.upper().endswith('USDT'):
            base = pair.upper().replace('USDT', '')
            return f"B-{base}_USDT"
        elif pair.upper().endswith('BTC'):
            base = pair.upper().replace('BTC', '')
            return f"B-{base}_BTC"
        elif pair.upper().endswith('INR'):
            base = pair.upper().replace('INR', '')
            return f"I-{base}_INR"
        else:
            # Default fallback
            return f"B-{pair.upper()}"

    # Public endpoints
    def get_ticker(self) -> Dict[str, Any]:
        """Get ticker data for all markets."""
        return self._make_public_request("/exchange/ticker")

    def get_markets(self) -> Dict[str, Any]:
        """Get all available markets."""
        return self._make_public_request("/exchange/v1/markets")

    def get_market_details(self, pair: str = None) -> Dict[str, Any]:
        """Get market details. If pair is specified, filter for that specific trading pair."""
        all_markets = self._make_public_request("/exchange/v1/markets_details")
        
        if pair:
            # Filter for the specific pair
            for market in all_markets:
                if (market.get("coindcx_name", "").upper() == pair.upper() or 
                    market.get("symbol", "").upper() == pair.upper() or
                    market.get("pair", "").upper() == f"KC-{pair.upper().replace('USDT', '_USDT')}" or
                    market.get("pair", "").upper() == f"KC-{pair.upper().replace('BTC', '_BTC')}"):
                    return market
            
            # If not found, return error message
            return {"error": f"Trading pair '{pair}' not found"}
        
        return all_markets

    def get_trades(self, pair: str, limit: int = 30) -> Dict[str, Any]:
        """Get recent trades for a market."""
        # Convert pair format from BTCUSDT to B-BTC_USDT
        formatted_pair = self._format_pair_for_public_api(pair)
        params = {"pair": formatted_pair, "limit": limit}
        return self._make_public_market_data_request("/market_data/trade_history", params)

    def get_order_book(self, pair: str) -> Dict[str, Any]:
        """Get order book for a market."""
        # Convert pair format from BTCUSDT to B-BTC_USDT
        formatted_pair = self._format_pair_for_public_api(pair)
        params = {"pair": formatted_pair}
        return self._make_public_market_data_request("/market_data/orderbook", params)

    def get_candles(self, pair: str, interval: str, start_time: int, end_time: int, limit: int = 1000) -> Dict[str, Any]:
        """Get candlestick data."""
        # Convert pair format from BTCUSDT to B-BTC_USDT
        formatted_pair = self._format_pair_for_public_api(pair)
        params = {
            "pair": formatted_pair,
            "interval": interval,
            "limit": limit
        }
        
        # Only add time parameters if they seem reasonable
        # Check if start_time is not in the future or too far in the past
        current_time = int(time.time() * 1000)
        one_year_ago = current_time - (365 * 24 * 60 * 60 * 1000)
        
        # Add time parameters only if they're within a reasonable range
        if start_time >= one_year_ago and start_time <= current_time and end_time <= current_time:
            params["startTime"] = start_time
            params["endTime"] = end_time
        
        result = self._make_public_market_data_request("/market_data/candles", params)
        
        # If no data returned with time params, try without time constraints
        if isinstance(result, list) and len(result) == 0 and ("startTime" in params or "endTime" in params):
            # Remove time parameters and try again
            params_no_time = {
                "pair": formatted_pair,
                "interval": interval,
                "limit": limit
            }
            result = self._make_public_market_data_request("/market_data/candles", params_no_time)
            
            # Add a note about the fallback
            if isinstance(result, list) and len(result) > 0:
                return {
                    "data": result,
                    "note": f"No data found for specified time range ({start_time} to {end_time}). Returning most recent {len(result)} candles instead.",
                    "requested_start_time": start_time,
                    "requested_end_time": end_time
                }
        
        return result

    # User endpoints
    def get_balances(self) -> Dict[str, Any]:
        """Get account balances."""
        return self._make_authenticated_request("POST", "/exchange/v1/users/balances")

    def get_user_info(self) -> Dict[str, Any]:
        """Get user information."""
        return self._make_authenticated_request("POST", "/exchange/v1/users/info")

    # Order endpoints
    def create_order(self, side: str, order_type: str, market: str, price: float = None, 
                    quantity: float = None, total_quantity: float = None, 
                    client_order_id: str = None) -> Dict[str, Any]:
        """Create a new order."""
        payload = {
            "side": side,
            "order_type": order_type,
            "market": market
        }
        
        if price is not None:
            payload["price_per_unit"] = price
        if quantity is not None:
            payload["quantity"] = quantity
        if total_quantity is not None:
            payload["total_quantity"] = total_quantity
        if client_order_id is not None:
            payload["client_order_id"] = client_order_id
            
        return self._make_authenticated_request("POST", "/exchange/v1/orders/create", payload)

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status."""
        payload = {"id": order_id}
        return self._make_authenticated_request("POST", "/exchange/v1/orders/status", payload)

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order."""
        payload = {"id": order_id}
        return self._make_authenticated_request("POST", "/exchange/v1/orders/cancel", payload)

    def get_active_orders(self, market: str = None, side: str = None) -> Dict[str, Any]:
        """Get active orders."""
        payload = {}
        if market:
            payload["market"] = market
        if side:
            payload["side"] = side
        return self._make_authenticated_request("POST", "/exchange/v1/orders/active_orders", payload)

    def get_order_history(self, market: str = None, side: str = None, 
                         from_timestamp: int = None, to_timestamp: int = None, 
                         limit: int = 500) -> Dict[str, Any]:
        """Get order history."""
        payload = {"limit": limit}
        if market:
            payload["market"] = market
        if side:
            payload["side"] = side
        if from_timestamp:
            payload["from"] = from_timestamp
        if to_timestamp:
            payload["to"] = to_timestamp
        return self._make_authenticated_request("POST", "/exchange/v1/orders", payload)

    def close(self):
        """Close the HTTP client."""
        self.client.close()