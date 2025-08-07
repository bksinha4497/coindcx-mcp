import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration settings for CoinDCX MCP server."""
    
    def __init__(self):
        self.api_key = os.getenv("COINDCX_API_KEY", "")
        self.secret_key = os.getenv("COINDCX_SECRET_KEY", "")
        self.base_url = os.getenv("COINDCX_BASE_URL", "https://api.coindcx.com")
        self.sandbox_mode = os.getenv("COINDCX_SANDBOX_MODE", "false").lower() == "true"
        
    def validate(self) -> bool:
        """Validate that required configuration is present."""
        return bool(self.api_key and self.secret_key)
    
    def get_missing_config(self) -> list[str]:
        """Get list of missing required configuration items."""
        missing = []
        if not self.api_key:
            missing.append("COINDCX_API_KEY")
        if not self.secret_key:
            missing.append("COINDCX_SECRET_KEY")
        return missing


config = Config()
