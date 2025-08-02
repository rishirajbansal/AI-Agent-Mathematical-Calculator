"""
Base classes for tools
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from models.schemas import ToolResult, ToolDefinition


class BaseTool(ABC):
    """Abstract base class for all tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    def get_tool_definition(self) -> ToolDefinition:
        """Get the tool definition for OpenAI function calling"""
        pass
    
    def _create_success_result(self, result: Any) -> ToolResult:
        """Helper method to create successful result"""
        return ToolResult(success=True, result=result)
    
    def _create_error_result(self, error: str) -> ToolResult:
        """Helper method to create error result"""
        return ToolResult(success=False, result=None, error=error)