"""
Configuration settings for the AI Agent
"""
import os
from dotenv import load_dotenv
from typing import Dict, Any
from dataclasses import dataclass

load_dotenv()

@dataclass
class AgentConfig:
    """Configuration class for AI Agent settings"""
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000
    max_iterations: int = 10
    
    def __post_init__(self):
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

# Global configuration instance
config = AgentConfig()

# Tool configurations
TOOL_CONFIG: Dict[str, Any] = {
    "calculator": {
        "name": "calculator",
        "description": "Perform mathematical calculations",
        "enabled": True
    },
    "web_search": {
        "name": "web_search", 
        "description": "Search the web for information",
        "enabled": False  # Requires additional setup
    },
    "file_operations": {
        "name": "file_operations",
        "description": "Read and write files",
        "enabled": True
    }
}