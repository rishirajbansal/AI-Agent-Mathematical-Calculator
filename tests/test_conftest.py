"""
Pytest configuration and fixtures
"""
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Generator, Dict, Any

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice

from models.schemas import Message, MessageRole, ToolDefinition, AgentResponse
from core.agent import AIAgent
from core.llm_client import LLMClient
from tools.calculator import CalculatorTool
from tools.file_operations import FileOperationsTool
from tools.manager import ToolManager


@pytest.fixture
def temp_data_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for file operations testing"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    mock_client = Mock()
    
    # Mock successful response
    mock_choice = Choice(
        index=0,
        message=ChatCompletionMessage(
            role="assistant",
            content="Test response"
        ),
        finish_reason="stop"
    )
    
    mock_response = ChatCompletion(
        id="test_id",
        object="chat.completion",
        created=1234567890,
        model="gpt-4",
        choices=[mock_choice],
        usage=None
    )
    
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_llm_client(mock_openai_client):
    """Mock LLM client with mocked OpenAI client"""
    with pytest.mock.patch('core.llm_client.OpenAI') as mock_openai:
        mock_openai.return_value = mock_openai_client
        client = LLMClient()
        return client


@pytest.fixture
def calculator_tool():
    """Calculator tool instance for testing"""
    return CalculatorTool()


@pytest.fixture
def file_operations_tool(temp_data_dir):
    """File operations tool instance for testing"""
    return FileOperationsTool(allowed_directory=str(temp_data_dir))


@pytest.fixture
def tool_manager(calculator_tool, file_operations_tool):
    """Tool manager with mocked tools"""
    manager = ToolManager()
    manager.tools = {
        "calculator": calculator_tool,
        "file_operations": file_operations_tool
    }
    return manager


@pytest.fixture
def sample_messages():
    """Sample messages for testing"""
    return [
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant"),
        Message(role=MessageRole.USER, content="Hello"),
        Message(role=MessageRole.ASSISTANT, content="Hi there!")
    ]


@pytest.fixture
def mock_tool_definitions():
    """Mock tool definitions for testing"""
    return [
        ToolDefinition(
            type="function",
            function={
                "name": "calculator",
                "description": "Perform calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"}
                    },
                    "required": ["expression"]
                }
            }
        )
    ]


@pytest.fixture(autouse=True)
def mock_config():
    """Mock configuration for testing"""
    with pytest.mock.patch('config.settings.config') as mock_cfg:
        mock_cfg.openai_api_key = "test_key"
        mock_cfg.model = "gpt-4"
        mock_cfg.temperature = 0.7
        mock_cfg.max_tokens = 1000
        mock_cfg.max_iterations = 10
        yield mock_cfg


@pytest.fixture
def ai_agent(mock_llm_client, tool_manager):
    """AI Agent instance for testing"""
    with pytest.mock.patch('core.agent.LLMClient') as mock_client_class:
        mock_client_class.return_value = mock_llm_client
        with pytest.mock.patch('core.agent.ToolManager') as mock_manager_class:
            mock_manager_class.return_value = tool_manager
            agent = AIAgent()
            return agent


# Test data factories
class MessageFactory:
    """Factory for creating test messages"""
    
    @staticmethod
    def user_message(content: str = "Test user message") -> Message:
        return Message(role=MessageRole.USER, content=content)
    
    @staticmethod
    def assistant_message(content: str = "Test assistant message") -> Message:
        return Message(role=MessageRole.ASSISTANT, content=content)
    
    @staticmethod
    def system_message(content: str = "Test system message") -> Message:
        return Message(role=MessageRole.SYSTEM, content=content)
    
    @staticmethod
    def tool_message(content: str = "Test tool result", tool_call_id: str = "test_id", name: str = "test_tool") -> Message:
        return Message(
            role=MessageRole.TOOL,
            content=content,
            tool_call_id=tool_call_id,
            name=name
        )


class ResponseFactory:
    """Factory for creating test responses"""
    
    @staticmethod
    def simple_response(content: str = "Test response") -> AgentResponse:
        return AgentResponse(content=content, finish_reason="stop")
    
    @staticmethod
    def tool_call_response(tool_name: str = "calculator", arguments: Dict[str, Any] = None) -> AgentResponse:
        if arguments is None:
            arguments = {"expression": "2+2"}
        
        return AgentResponse(
            content="I'll help you with that calculation.",
            tool_calls=[{
                "id": "test_call_id",
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": str(arguments)
                }
            }]
        )


# Make factories available as fixtures
@pytest.fixture
def message_factory():
    return MessageFactory


@pytest.fixture
def response_factory():
    return ResponseFactory