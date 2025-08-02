"""
Tool manager for handling all available tools
"""
from typing import Dict, List, Any
from tools.base import BaseTool
from tools.calculator import CalculatorTool
from tools.file_operations import FileOperationsTool
from models.schemas import ToolResult, ToolDefinition
from config.settings import TOOL_CONFIG


class ToolManager:
    """Manages all available tools for the agent"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all enabled tools"""
        # Initialize calculator tool
        if TOOL_CONFIG["calculator"]["enabled"]:
            self.tools["calculator"] = CalculatorTool()
        
        # Initialize file operations tool
        if TOOL_CONFIG["file_operations"]["enabled"]:
            self.tools["file_operations"] = FileOperationsTool()
        
        # Add more tools here as needed
    
    def get_available_tools(self) -> List[ToolDefinition]:
        """Get list of all available tool definitions"""
        return [tool.get_tool_definition() for tool in self.tools.values()]
    
    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a specific tool with given parameters"""
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                result=None,
                error=f"Tool '{tool_name}' not found"
            )
        
        return self.tools[tool_name].execute(**kwargs)
    
    def get_tool_names(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.tools.keys())
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool is available"""
        return tool_name in self.tools