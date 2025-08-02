"""
Data models and schemas for the AI Agent
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from enum import Enum


class MessageRole(str, Enum):
    """Enum for message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class Message(BaseModel):
    """Model for chat messages"""
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None


class ToolCall(BaseModel):
    """Model for tool calls"""
    id: str
    type: Literal["function"] = "function"
    function: Dict[str, Any]


class AgentResponse(BaseModel):
    """Model for agent responses"""
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    finish_reason: Optional[str] = None


class ToolDefinition(BaseModel):
    """Model for tool definitions"""
    type: Literal["function"] = "function"
    function: Dict[str, Any]


class AgentState(BaseModel):
    """Model for agent state"""
    messages: List[Message] = Field(default_factory=list)
    iteration_count: int = 0
    is_complete: bool = False
    final_response: Optional[str] = None


class ToolResult(BaseModel):
    """Model for tool execution results"""
    success: bool
    result: Any
    error: Optional[str] = None