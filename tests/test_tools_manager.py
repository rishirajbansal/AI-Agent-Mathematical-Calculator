"""
Tests for Tool Manager
"""
import pytest
from unittest.mock import patch, Mock

from tools.manager import ToolManager
from tools.calculator import CalculatorTool
from tools.file_operations import FileOperationsTool
from models.schemas import ToolDefinition, ToolResult


class TestToolManager:
    """Test Tool Manager functionality"""
    
    @pytest.fixture
    def mock_tool_config(self):
        """Mock tool configuration"""
        return {
            "calculator": {"enabled": True},
            "file_operations": {"enabled": True},
            "web_search": {"enabled": False}
        }
    
    @patch('tools.manager.TOOL_CONFIG')
    def test_initialization(self, mock_config, mock_tool_config):
        """Test tool manager initialization"""
        mock_config.__getitem__.side_effect = lambda key: mock_tool_config[key]
        
        manager = ToolManager()
        
        assert "calculator" in manager.tools
        assert "file_operations" in manager.tools
        assert isinstance(manager.tools["calculator"], CalculatorTool)
        assert isinstance(manager.tools["file_operations"], FileOperationsTool)
    
    @patch('tools.manager.TOOL_CONFIG')
    def test_disabled_tools_not_loaded(self, mock_config, mock_tool_config):
        """Test that disabled tools are not loaded"""
        # Disable calculator tool
        mock_tool_config["calculator"]["enabled"] = False
        mock_config.__getitem__.side_effect = lambda key: mock_tool_config[key]
        
        manager = ToolManager()
        
        assert "calculator" not in manager.tools
        assert "file_operations" in manager.tools
        assert len(manager.tools) == 1
    
    def test_get_available_tools(self, tool_manager):
        """Test getting available tool definitions"""
        definitions = tool_manager.get_available_tools()
        
        assert isinstance(definitions, list)
        assert len(definitions) == 2  # calculator and file_operations
        
        for definition in definitions:
            assert isinstance(definition, ToolDefinition)
            assert definition.type == "function"
            assert "name" in definition.function
            assert "description" in definition.function
    
    def test_execute_tool_success(self, tool_manager):
        """Test successful tool execution"""
        result = tool_manager.execute_tool("calculator", expression="2 + 2")
        
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.result == 4
        assert result.error is None
    
    def test_execute_tool_error(self, tool_manager):
        """Test tool execution with error"""
        result = tool_manager.execute_tool("calculator", expression="1 / 0")
        
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert result.error is not None
    
    def test_execute_nonexistent_tool(self, tool_manager):
        """Test executing a tool that doesn't exist"""
        result = tool_manager.execute_tool("nonexistent_tool", param="value")
        
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert "Tool 'nonexistent_tool' not found" in result.error
    
    def test_get_tool_names(self, tool_manager):
        """Test getting list of tool names"""
        names = tool_manager.get_tool_names()
        
        assert isinstance(names, list)
        assert "calculator" in names
        assert "file_operations" in names
        assert len(names) == 2
    
    def test_has_tool(self, tool_manager):
        """Test checking if tool exists"""
        assert tool_manager.has_tool("calculator") is True
        assert tool_manager.has_tool("file_operations") is True
        assert tool_manager.has_tool("nonexistent_tool") is False
    
    def test_empty_tool_manager(self):
        """Test tool manager with no tools"""
        with patch('tools.manager.TOOL_CONFIG', {
            "calculator": {"enabled": False},
            "file_operations": {"enabled": False}
        }):
            manager = ToolManager()
            
            assert len(manager.tools) == 0
            assert manager.get_tool_names() == []
            assert manager.get_available_tools() == []
            assert manager.has_tool("calculator") is False
    
    def test_tool_execution_with_kwargs(self, tool_manager):
        """Test tool execution with keyword arguments"""
        # Test file operations tool
        result = tool_manager.execute_tool(
            "file_operations",
            action="list",
            filename=""
        )
        
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert isinstance(result.result, list)
    
    def test_tool_execution_missing_params(self, tool_manager):
        """Test tool execution with missing parameters"""
        # Calculator tool requires 'expression' parameter
        result = tool_manager.execute_tool("calculator")
        
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert result.error is not None