"""
Tests for LLM Client
"""
import pytest
from unittest.mock import Mock, patch
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_message_tool_call import Function

from core.llm_client import LLMClient
from models.schemas import Message, MessageRole, AgentResponse, ToolDefinition


class TestLLMClient:
    """Test LLM Client functionality"""
    
    @pytest.fixture
    def llm_client(self, mock_openai_client):
        """LLM client fixture"""
        with patch('core.llm_client.OpenAI') as mock_openai:
            mock_openai.return_value = mock_openai_client
            return LLMClient()
    
    def test_initialization(self, llm_client):
        """Test LLM client initialization"""
        assert llm_client.model == "gpt-4"  # From mock config
        assert llm_client.temperature == 0.7
        assert llm_client.max_tokens == 1000
    
    def test_simple_response(self, llm_client, mock_openai_client, sample_messages):
        """Test generating a simple response"""
        # Mock response
        mock_choice = Choice(
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                content="Hello! How can I help you?"
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
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        response = llm_client.generate_response(sample_messages)
        
        assert isinstance(response, AgentResponse)
        assert response.content == "Hello! How can I help you?"
        assert response.tool_calls is None
        assert response.finish_reason == "stop"
    
    def test_response_with_tool_calls(self, llm_client, mock_openai_client, sample_messages):
        """Test generating response with tool calls"""
        # Mock tool call
        mock_tool_call = ChatCompletionMessageToolCall(
            id="call_123",
            type="function",
            function=Function(
                name="calculator",
                arguments='{"expression": "2+2"}'
            )
        )
        
        mock_choice = Choice(
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                content="I'll calculate that for you.",
                tool_calls=[mock_tool_call]
            ),
            finish_reason="tool_calls"
        )
        mock_response = ChatCompletion(
            id="test_id",
            object="chat.completion",
            created=1234567890,
            model="gpt-4",
            choices=[mock_choice],
            usage=None
        )
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        response = llm_client.generate_response(sample_messages)
        
        assert isinstance(response, AgentResponse)
        assert response.content == "I'll calculate that for you."
        assert response.tool_calls is not None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].id == "call_123"
        assert response.tool_calls[0].function["name"] == "calculator"
        assert response.finish_reason == "tool_calls"
    
    def test_generate_response_with_tools(self, llm_client, mock_openai_client, sample_messages, mock_tool_definitions):
        """Test generating response with tool definitions"""
        mock_choice = Choice(
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                content="I can help with calculations."
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
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        response = llm_client.generate_response(sample_messages, mock_tool_definitions)
        
        # Verify API was called with tools
        call_args = mock_openai_client.chat.completions.create.call_args
        assert "tools" in call_args.kwargs
        assert "tool_choice" in call_args.kwargs
        assert call_args.kwargs["tool_choice"] == "auto"
    
    def test_message_conversion(self, llm_client):
        """Test converting Message objects to OpenAI format"""
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are helpful"),
            Message(role=MessageRole.USER, content="Hello"),
            Message(role=MessageRole.ASSISTANT, content="Hi there!"),
            Message(
                role=MessageRole.TOOL,
                content="42",
                tool_call_id="call_123",
                name="calculator"
            )
        ]
        
        converted = [llm_client._message_to_dict(msg) for msg in messages]
        
        assert converted[0] == {"role": "system", "content": "You are helpful"}
        assert converted[1] == {"role": "user", "content": "Hello"}
        assert converted[2] == {"role": "assistant", "content": "Hi there!"}
        assert converted[3] == {
            "role": "tool",
            "content": "42",
            "tool_call_id": "call_123",
            "name": "calculator"
        }
    
    def test_api_error_handling(self, llm_client, mock_openai_client, sample_messages):
        """Test handling API errors"""
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="LLM API error: API Error"):
            llm_client.generate_response(sample_messages)
    
    def test_empty_content_response(self, llm_client, mock_openai_client, sample_messages):
        """Test handling response with empty content"""
        mock_choice = Choice(
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                content=None  # Empty content
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
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        response = llm_client.generate_response(sample_messages)
        
        assert response.content == ""  # Should handle None content
    
    def test_request_parameters(self, llm_client, mock_openai_client, sample_messages):
        """Test that correct parameters are sent to API"""
        mock_choice = Choice(
            index=0,
            message=ChatCompletionMessage(role="assistant", content="test"),
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
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        llm_client.generate_response(sample_messages)
        
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "gpt-4"
        assert call_args.kwargs["temperature"] == 0.7
        assert call_args.kwargs["max_tokens"] == 1000
        assert len(call_args.kwargs["messages"]) == len(sample_messages)
    
    def test_multiple_tool_calls(self, llm_client, mock_openai_client, sample_messages):
        """Test handling multiple tool calls in response"""
        mock_tool_calls = [
            ChatCompletionMessageToolCall(
                id="call_1",
                type="function",
                function=Function(name="calculator", arguments='{"expression": "2+2"}')
            ),
            ChatCompletionMessageToolCall(
                id="call_2", 
                type="function",
                function=Function(name="calculator", arguments='{"expression": "3*3"}')
            )
        ]
        
        mock_choice = Choice(
            index=0,
            message=ChatCompletionMessage(
                role="assistant",
                content="I'll perform both calculations.",
                tool_calls=mock_tool_calls
            ),
            finish_reason="tool_calls"
        )
        mock_response = ChatCompletion(
            id="test_id",
            object="chat.completion",
            created=1234567890,
            model="gpt-4",
            choices=[mock_choice],
            usage=None
        )
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        response = llm_client.generate_response(sample_messages)
        
        assert len(response.tool_calls) == 2
        assert response.tool_calls[0].id == "call_1"
        assert response.tool_calls[1].id == "call_2"