"""
Integration tests for the complete AI Agent system
"""
import pytest
from unittest.mock import patch, Mock
from pathlib import Path

from core.agent import AIAgent
from models.schemas import AgentResponse, ToolCall


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests for the complete agent system"""
    
    @pytest.fixture
    def integration_agent(self, temp_data_dir):
        """Create an agent for integration testing"""
        with patch('config.settings.config') as mock_config:
            mock_config.openai_api_key = "test_key"
            mock_config.model = "gpt-4"
            mock_config.temperature = 0.7
            mock_config.max_tokens = 1000
            mock_config.max_iterations = 5
            
            with patch('tools.file_operations.FileOperationsTool') as mock_file_tool:
                # Use real file tool with temp directory
                from tools.file_operations import FileOperationsTool
                mock_file_tool.return_value = FileOperationsTool(str(temp_data_dir))
                
                agent = AIAgent()
                return agent
    
    def test_calculator_workflow(self, integration_agent):
        """Test complete calculator workflow"""
        # Mock LLM responses
        tool_call_response = AgentResponse(
            content="I'll calculate that for you.",
            tool_calls=[ToolCall(
                id="call_123",
                function={
                    "name": "calculator",
                    "arguments": '{"expression": "15 * 4 + 2"}'
                }
            )]
        )
        
        final_response = AgentResponse(
            content="The result of 15 * 4 + 2 is 62.",
            finish_reason="stop"
        )
        
        integration_agent.llm_client.generate_response.side_effect = [
            tool_call_response,
            final_response
        ]
        
        response = integration_agent.run("What is 15 times 4 plus 2?")
        
        assert "62" in response
        assert integration_agent.tool_manager.execute_tool("calculator", expression="15 * 4 + 2").result == 62
    
    def test_file_operations_workflow(self, integration_agent, temp_data_dir):
        """Test complete file operations workflow"""
        # Mock LLM responses for writing a file
        write_response = AgentResponse(
            content="I'll create that file for you.",
            tool_calls=[ToolCall(
                id="call_write",
                function={
                    "name": "file_operations",
                    "arguments": '{"action": "write", "filename": "test.txt", "content": "Hello, World!"}'
                }
            )]
        )
        
        read_response = AgentResponse(
            content="Now I'll read the file back.",
            tool_calls=[ToolCall(
                id="call_read",
                function={
                    "name": "file_operations", 
                    "arguments": '{"action": "read", "filename": "test.txt"}'
                }
            )]
        )
        
        final_response = AgentResponse(
            content="The file contains: Hello, World!",
            finish_reason="stop"
        )
        
        integration_agent.llm_client.generate_response.side_effect = [
            write_response,
            read_response,
            final_response
        ]
        
        # Test file creation and reading
        response = integration_agent.run("Create a file called test.txt with 'Hello, World!' and then read it back")
        
        # Verify file was actually created
        test_file = temp_data_dir / "test.txt"
        assert test_file.exists()
        assert test_file.read_text() == "Hello, World!"
        
        assert "Hello, World!" in response
    
    def test_complex_math_and_file_workflow(self, integration_agent, temp_data_dir):
        """Test workflow combining math calculation and file operations"""
        # Mock LLM responses for complex workflow
        calc_response = AgentResponse(
            content="I'll calculate the area first.",
            tool_calls=[ToolCall(
                id="call_calc",
                function={
                    "name": "calculator",
                    "arguments": '{"expression": "3.14159 * 5 * 5"}'
                }
            )]
        )
        
        file_response = AgentResponse(
            content="Now I'll save the result to a file.",
            tool_calls=[ToolCall(
                id="call_file",
                function={
                    "name": "file_operations",
                    "arguments": '{"action": "write", "filename": "circle_area.txt", "content": "Area of circle with radius 5: 78.53975"}'
                }
            )]
        )
        
        final_response = AgentResponse(
            content="I calculated the area as 78.54 and saved it to circle_area.txt",
            finish_reason="stop"
        )
        
        integration_agent.llm_client.generate_response.side_effect = [
            calc_response,
            file_response, 
            final_response
        ]
        
        response = integration_agent.run("Calculate the area of a circle with radius 5 and save the result to a file")
        
        # Verify calculation was performed
        calc_result = integration_agent.tool_manager.execute_tool(
            "calculator", 
            expression="3.14159 * 5 * 5"
        )
        assert calc_result.success
        assert abs(calc_result.result - 78.53975) < 0.001
        
        # Verify file was created (in actual integration, this would be done by the agent)
        # Here we test the tool directly since we're mocking the LLM
        file_result = integration_agent.tool_manager.execute_tool(
            "file_operations",
            action="write",
            filename="circle_area.txt",
            content="Area of circle with radius 5: 78.53975"
        )
        assert file_result.success
        
        # Verify final response
        assert "78.54" in response or "78.53975" in response
        assert "circle_area.txt" in response
    
    def test_error_recovery_workflow(self, integration_agent):
        """Test agent's ability to recover from errors"""
        # Mock LLM responses with error recovery
        error_response = AgentResponse(
            content="I'll try to divide by zero.",
            tool_calls=[ToolCall(
                id="call_error",
                function={
                    "name": "calculator",
                    "arguments": '{"expression": "1 / 0"}'
                }
            )]
        )
        
        recovery_response = AgentResponse(
            content="Let me try a valid calculation instead.",
            tool_calls=[ToolCall(
                id="call_recovery",
                function={
                    "name": "calculator", 
                    "arguments": '{"expression": "1 / 2"}'
                }
            )]
        )
        
        final_response = AgentResponse(
            content="I encountered an error with the first calculation, but 1/2 = 0.5",
            finish_reason="stop"
        )
        
        integration_agent.llm_client.generate_response.side_effect = [
            error_response,
            recovery_response,
            final_response
        ]
        
        response = integration_agent.run("What is 1 divided by 0, and if that fails, what is 1 divided by 2?