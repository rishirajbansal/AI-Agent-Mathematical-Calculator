"""
Tests for AI Agent core functionality
"""
import json
import pytest
from unittest.mock import Mock, patch, MagicMock

from core.agent import AIAgent
from models.schemas import (
    Message, MessageRole, AgentResponse, ToolCall, ToolResult
)


class TestAIAgent:
    """Test AI Agent functionality"""
    
    @pytest.fixture
    def mock_llm_response_simple(self):
        """Mock simple LLM response without tool calls"""
        return AgentResponse(
            content="Hello! How can I help you today?",
            finish_reason="stop"
        )
    
    @pytest.fixture  
    def mock_llm_response_with_tool_call(self):
        """Mock LLM response with tool call"""
        return AgentResponse(
            content="I'll calculate that for you.",
            tool_calls=[ToolCall(
                id="call_123",
                function={
                    "name": "calculator",
                    "arguments": '{"expression": "2+2"}'
                }
            )],
            finish_reason="tool_calls"
        )
    
    def test_initialization(self, ai_agent):
        """Test agent initialization"""
        assert ai_agent.llm_client is not None
        assert ai_agent.tool_manager is not None
        assert ai_agent.system_prompt is not None
        assert "helpful AI assistant" in ai_agent.system_prompt
    
    def test_system_prompt_generation(self, ai_agent, tool_manager):
        """Test system prompt includes available tools"""
        tool_manager.get_tool_names.return_value = ["calculator", "file_operations"]
        
        prompt = ai_agent._get_system_prompt()
        
        assert "calculator, file_operations" in prompt
        assert "helpful AI assistant" in prompt
        assert "tool" in prompt.lower()
    
    def test_simple_conversation(self, ai_agent, mock_llm_response_simple):
        """Test simple conversation without tool calls"""
        ai_agent.llm_client.generate_response.return_value = mock_llm_response_simple
        
        response = ai_agent.run("Hello, how are you?")
        
        assert response == "Hello! How can I help you today?"
        ai_agent.llm_client.generate_response.assert_called_once()
    
    def test_conversation_with_tool_call(self, ai_agent, mock_llm_response_with_tool_call):
        """Test conversation that requires tool execution"""
        # Mock tool execution result
        tool_result = ToolResult(success=True, result=4)
        ai_agent.tool_manager.execute_tool.return_value = tool_result
        
        # Mock second LLM response after tool execution
        final_response = AgentResponse(
            content="The result of 2+2 is 4.",
            finish_reason="stop"
        )
        
        ai_agent.llm_client.generate_response.side_effect = [
            mock_llm_response_with_tool_call,
            final_response
        ]
        
        response = ai_agent.run("What is 2+2?")
        
        assert response == "The result of 2+2 is 4."
        assert ai_agent.llm_client.generate_response.call_count == 2
        ai_agent.tool_manager.execute_tool.assert_called_once_with(
            "calculator", expression="2+2"
        )
    
    def test_tool_execution_error(self, ai_agent, mock_llm_response_with_tool_call):
        """Test handling tool execution errors"""
        # Mock tool execution error
        tool_result = ToolResult(
            success=False,
            result=None,
            error="Division by zero"
        )
        ai_agent.tool_manager.execute_tool.return_value = tool_result
        
        # Mock final response
        final_response = AgentResponse(
            content="I encountered an error: Division by zero",
            finish_reason="stop"
        )
        
        ai_agent.llm_client.generate_response.side_effect = [
            mock_llm_response_with_tool_call,
            final_response
        ]
        
        response = ai_agent.run("What is 1/0?")
        
        assert "error" in response.lower()
        ai_agent.tool_manager.execute_tool.assert_called_once()
    
    def test_conversation_history(self, ai_agent, mock_llm_response_simple):
        """Test conversation with history"""
        history = [
            Message(role=MessageRole.USER, content="Previous question"),
            Message(role=MessageRole.ASSISTANT, content="Previous answer")
        ]
        
        ai_agent.llm_client.generate_response.return_value = mock_llm_response_simple
        
        response = ai_agent.run("Follow-up question", conversation_history=history)
        
        # Check that history was included in the call
        call_args = ai_agent.llm_client.generate_response.call_args[0][0]
        messages_content = [msg.content for msg in call_args]
        
        assert "Previous question" in messages_content
        assert "Previous answer" in messages_content
        assert "Follow-up question" in messages_content
    
    def test_max_iterations_limit(self, ai_agent):
        """Test that agent stops after max iterations"""
        # Mock responses that always require tool calls
        tool_call_response = AgentResponse(
            content="I need to use a tool.",
            tool_calls=[ToolCall(
                id="call_123",
                function={
                    "name": "calculator", 
                    "arguments": '{"expression": "1+1"}'
                }
            )],
            finish_reason="tool_calls"
        )
        
        ai_agent.llm_client.generate_response.return_value = tool_call_response
        ai_agent.tool_manager.execute_tool.return_value = ToolResult(
            success=True, result=2
        )
        
        with patch('config.settings.config.max_iterations', 2):
            response = ai_agent.run("Test question")
            
            assert "couldn't complete the task" in response
            assert ai_agent.llm_client.generate_response.call_count == 2
    
    def test_json_parsing_error_in_tool_call(self, ai_agent):
        """Test handling JSON parsing errors in tool calls"""
        # Mock response with invalid JSON in tool call
        tool_call_response = AgentResponse(
            content="I'll help with that.",
            tool_calls=[ToolCall(
                id="call_123",
                function={
                    "name": "calculator",
                    "arguments": 'invalid json{'  # Invalid JSON
                }
            )],
            finish_reason="tool_calls"
        )
        
        final_response = AgentResponse(
            content="I apologize for the error.",
            finish_reason="stop"
        )
        
        ai_agent.llm_client.generate_response.side_effect = [
            tool_call_response,
            final_response
        ]
        
        response = ai_agent.run("Test question")
        
        # Should handle the error gracefully
        assert response == "I apologize for the error."
    
    def test_multiple_tool_calls(self, ai_agent):
        """Test handling multiple tool calls in one response"""
        tool_calls = [
            ToolCall(
                id="call_1",
                function={
                    "name": "calculator",
                    "arguments": '{"expression": "2+2"}'
                }
            ),
            ToolCall(
                id="call_2", 
                function={
                    "name": "calculator",
                    "arguments": '{"expression": "3*3"}'
                }
            )
        ]
        
        multi_tool_response = AgentResponse(
            content="I'll perform both calculations.",
            tool_calls=tool_calls,
            finish_reason="tool_calls"
        )
        
        final_response = AgentResponse(
            content="The results are 4 and 9.",
            finish_reason="stop"
        )
        
        ai_agent.llm_client.generate_response.side_effect = [
            multi_tool_response,
            final_response
        ]
        
        ai_agent.tool_manager.execute_tool.side_effect = [
            ToolResult(success=True, result=4),
            ToolResult(success=True, result=9)
        ]
        
        response = ai_agent.run("Calculate 2+2 and 3*3")
        
        assert response == "The results are 4 and 9."
        assert ai_agent.tool_manager.execute_tool.call_count == 2
    
    def test_system_message_insertion(self, ai_agent, mock_llm_response_simple):
        """Test that system message is inserted at the beginning"""
        ai_agent.llm_client.generate_response.return_value = mock_llm_response_simple
        
        ai_agent.run("Test question")
        
        call_args = ai_agent.llm_client.generate_response.call_args[0][0]
        first_message = call_args[0]
        
        assert first_message.role == MessageRole.SYSTEM
        assert "helpful AI assistant" in first_message.content
    
    def test_existing_system_message_not_duplicated(self, ai_agent, mock_llm_response_simple):
        """Test that existing system message is not duplicated"""
        history = [
            Message(role=MessageRole.SYSTEM, content="Existing system message"),
            Message(role=MessageRole.USER, content="Previous question")
        ]
        
        ai_agent.llm_client.generate_response.return_value = mock_llm_response_simple
        
        ai_agent.run("New question", conversation_history=history)
        
        call_args = ai_agent.llm_client.generate_response.call_args[0][0]
        system_messages = [msg for msg in call_args if msg.role == MessageRole.SYSTEM]
        
        assert len(system_messages) == 1
        assert system_messages[0].content == "Existing system message"
    
    def test_empty_user_input(self, ai_agent, mock_llm_response_simple):
        """Test handling empty user input"""
        ai_agent.llm_client.generate_response.return_value = mock_llm_response_simple
        
        response = ai_agent.run("")
        
        assert response == "Hello! How can I help you today?"
        # Should still process empty input normally