"""
LLM client for interacting with OpenAI API
"""
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from models.schemas import Message, AgentResponse, ToolCall, ToolDefinition
from config.settings import config


class LLMClient:
    """Client for interacting with OpenAI LLM"""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.openai_api_key)
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
    
    def generate_response(
        self, 
        messages: List[Message], 
        tools: Optional[List[ToolDefinition]] = None
    ) -> AgentResponse:
        """Generate response from LLM"""
        try:
            # Convert messages to OpenAI format
            openai_messages = [self._message_to_dict(msg) for msg in messages]
            
            # Prepare request parameters
            request_params = {
                "model": self.model,
                "messages": openai_messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # Add tools if provided
            if tools:
                request_params["tools"] = [tool.dict() for tool in tools]
                request_params["tool_choice"] = "auto"
            
            # Make API call
            response = self.client.chat.completions.create(**request_params)
            
            # Extract response data
            choice = response.choices[0]
            message = choice.message
            
            # Handle tool calls
            tool_calls = None
            if message.tool_calls:
                tool_calls = [
                    ToolCall(
                        id=tc.id,
                        type=tc.type,
                        function={
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    )
                    for tc in message.tool_calls
                ]
            
            return AgentResponse(
                content=message.content or "",
                tool_calls=tool_calls,
                finish_reason=choice.finish_reason
            )
            
        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")
    
    def _message_to_dict(self, message: Message) -> Dict[str, Any]:
        """Convert Message object to OpenAI API format"""
        msg_dict = {
            "role": message.role.value,
            "content": message.content
        }
        
        if message.name:
            msg_dict["name"] = message.name
        
        if message.tool_call_id:
            msg_dict["tool_call_id"] = message.tool_call_id
            
        return msg_dict