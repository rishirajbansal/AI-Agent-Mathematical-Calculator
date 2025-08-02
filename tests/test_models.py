"""
Tests for data models and schemas
"""
import pytest
from pydantic import ValidationError

from models.schemas import (
    Message, MessageRole, ToolCall, AgentResponse,
    ToolDefinition, AgentState, ToolResult
)


class TestMessage:
    """Test Message model"""
    
    def test_create_user_message(self):
        """Test creating a user message"""
        message = Message(role=MessageRole.USER, content="Hello")
        assert message.role == MessageRole.USER
        assert message.content == "Hello"
        assert message.name is None
        assert message.tool_call_id is None
    
    def test_create_tool_message(self):
        """Test creating a tool message"""
        message = Message(
            role=MessageRole.TOOL,
            content="Result",
            name="test_tool",
            tool_call_id="call_123"
        )
        assert message.role == MessageRole.TOOL
        assert message.content == "Result"
        assert message.name == "test_tool"
        assert message.tool_call_id == "call_123"
    
    def test_invalid_role(self):
        """Test invalid role raises validation error"""
        with pytest.raises(ValidationError):
            Message(role="invalid_role", content="test")


class TestToolCall:
    """Test ToolCall model"""
    
    def test_create_tool_call(self):
        """Test creating a tool call"""
        tool_call = ToolCall(
            id="call_123",
            function={"name": "calculator", "arguments": '{"expression": "2+2"}'}
        )
        assert tool_call.id == "call_123"
        assert tool_call.type == "function"
        assert tool_call.function["name"] == "calculator"
    
    def test_default_type(self):
        """Test default type is function"""
        tool_call = ToolCall(id="test", function={"name": "test"})
        assert tool_call.type == "function"


class TestAgentResponse:
    """Test AgentResponse model"""
    
    def test_simple_response(self):
        """Test simple response without tool calls"""
        response = AgentResponse(content="Hello", finish_reason="stop")
        assert response.content == "Hello"
        assert response.tool_calls is None
        assert response.finish_reason == "stop"
    
    def test_response_with_tool_calls(self):
        """Test response with tool calls"""
        tool_call = ToolCall(id="test", function={"name": "test"})
        response = AgentResponse(
            content="I'll help with that",
            tool_calls=[tool_call]
        )
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].id == "test"


class TestToolDefinition:
    """Test ToolDefinition model"""
    
    def test_create_tool_definition(self):
        """Test creating a tool definition"""
        definition = ToolDefinition(
            type="function",
            function={
                "name": "calculator",
                "description": "Perform calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"}
                    }
                }
            }
        )
        assert definition.type == "function"
        assert definition.function["name"] == "calculator"
    
    def test_default_type(self):
        """Test default type is function"""
        definition = ToolDefinition(function={"name": "test"})
        assert definition.type == "function"


class TestAgentState:
    """Test AgentState model"""
    
    def test_initial_state(self):
        """Test initial agent state"""
        state = AgentState()
        assert len(state.messages) == 0
        assert state.iteration_count == 0
        assert state.is_complete is False
        assert state.final_response is None
    
    def test_state_with_messages(self):
        """Test agent state with messages"""
        messages = [
            Message(role=MessageRole.USER, content="Hello"),
            Message(role=MessageRole.ASSISTANT, content="Hi")
        ]
        state = AgentState(messages=messages, iteration_count=2)
        assert len(state.messages) == 2
        assert state.iteration_count == 2
    
    def test_completed_state(self):
        """Test completed agent state"""
        state = AgentState(
            is_complete=True,
            final_response="Task completed"
        )
        assert state.is_complete is True
        assert state.final_response == "Task completed"


class TestToolResult:
    """Test ToolResult model"""
    
    def test_successful_result(self):
        """Test successful tool result"""
        result = ToolResult(success=True, result="42")
        assert result.success is True
        assert result.result == "42"
        assert result.error is None
    
    def test_error_result(self):
        """Test error tool result"""
        result = ToolResult(
            success=False,
            result=None,
            error="Division by zero"
        )
        assert result.success is False
        assert result.result is None
        assert result.error == "Division by zero"


class TestMessageRole:
    """Test MessageRole enum"""
    
    def test_all_roles_exist(self):
        """Test all expected roles exist"""
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
        assert MessageRole.SYSTEM == "system"
        assert MessageRole.TOOL == "tool"
    
    def test_role_membership(self):
        """Test role membership"""
        assert "user" in MessageRole
        assert "assistant" in MessageRole
        assert "system" in MessageRole
        assert "tool" in MessageRole
        assert "invalid" not in MessageRole