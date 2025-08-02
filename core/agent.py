"""
Main AI Agent implementation
"""
import json
from typing import List, Optional
from core.llm_client import LLMClient
from tools.manager import ToolManager
from models.schemas import (
    Message, MessageRole, AgentState, ToolCall
)
from config.settings import config


class AIAgent:
    """Main AI Agent class"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.tool_manager = ToolManager()
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        available_tools = self.tool_manager.get_tool_names()
        tools_description = ", ".join(available_tools) if available_tools else "None"
        
        return f"""You are a helpful AI assistant with access to the following tools: {tools_description}.

When a user asks you to perform a task that requires using tools, you should:
1. Analyze the user's request
2. Determine which tool(s) to use
3. Call the appropriate tool(s) with the correct parameters
4. Provide a helpful response based on the tool results

Always be helpful, accurate, and provide clear explanations of your actions.
If you encounter an error, explain what went wrong and suggest alternatives when possible."""
    
    def run(self, user_input: str, conversation_history: Optional[List[Message]] = None) -> str:
        """Run the agent with user input"""
        # Initialize state
        state = AgentState()
        
        # Add conversation history if provided
        if conversation_history:
            state.messages.extend(conversation_history)
        
        # Add system message if this is the start of conversation
        if not state.messages or state.messages[0].role != MessageRole.SYSTEM:
            state.messages.insert(0, Message(
                role=MessageRole.SYSTEM,
                content=self.system_prompt
            ))
        
        # Add user message
        state.messages.append(Message(
            role=MessageRole.USER,
            content=user_input
        ))
        
        # Process until completion or max iterations
        while not state.is_complete and state.iteration_count < config.max_iterations:
            state.iteration_count += 1
            
            # Generate response from LLM
            response = self.llm_client.generate_response(
                messages=state.messages,
                tools=self.tool_manager.get_available_tools()
            )
            
            # Handle tool calls
            if response.tool_calls:
                self._handle_tool_calls(state, response.tool_calls)
            else:
                # No tool calls, this is the final response
                state.is_complete = True
                state.final_response = response.content
                
                # Add assistant message to history
                state.messages.append(Message(
                    role=MessageRole.ASSISTANT,
                    content=response.content
                ))
        
        return state.final_response or "Sorry, I couldn't complete the task within the allowed iterations."
    
    def _handle_tool_calls(self, state: AgentState, tool_calls: List[ToolCall]):
        """Handle tool calls from the LLM"""
        # Add assistant message with tool calls
        state.messages.append(Message(
            role=MessageRole.ASSISTANT,
            content="I'll help you with that. Let me use the appropriate tools."
        ))
        
        # Execute each tool call
        for tool_call in tool_calls:
            try:
                # Parse tool arguments
                tool_name = tool_call.function["name"]
                arguments = json.loads(tool_call.function["arguments"])
                
                # Execute tool
                result = self.tool_manager.execute_tool(tool_name, **arguments)
                
                # Format result for LLM
                if result.success:
                    content = str(result.result)
                else:
                    content = f"Error: {result.error}"
                
                # Add tool result message
                state.messages.append(Message(
                    role=MessageRole.TOOL,
                    content=content,
                    tool_call_id=tool_call.id,
                    name=tool_name
                ))
                
            except Exception as e:
                # Add error message
                state.messages.append(Message(
                    role=MessageRole.TOOL,
                    content=f"Error executing tool: {str(e)}",
                    tool_call_id=tool_call.id,
                    name=tool_call.function["name"]
                ))
    
    def get_conversation_history(self, state: AgentState) -> List[Message]:
        """Get conversation history from state"""
        return [msg for msg in state.messages if msg.role in [MessageRole.USER, MessageRole.ASSISTANT]]