"""Configuration module for ClarityForge."""

import os


class Config:
    """Configuration class for ClarityForge."""

    def __init__(self):
        """Initialize configuration with environment variables."""
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.api_host: str = os.getenv("API_HOST", "localhost")
        self.api_port: int = int(os.getenv("API_PORT", "8000"))
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

    @property
    def api_url(self) -> str:
        """Get the full API URL."""
        return f"http://{self.api_host}:{self.api_port}"


# Global configuration instance
config = Config()
