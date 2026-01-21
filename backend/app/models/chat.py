from pydantic import BaseModel
from enum import Enum
from typing import Optional


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    use_rag: bool = True  # Whether to use RAG for context
    prompt_key: str = "default"  # Which system prompt to use
    use_tools: bool = True  # Whether to enable agent tools (function calling)


class ToolCall(BaseModel):
    tool: str
    arguments: dict
    result: dict


class ChatResponse(BaseModel):
    message: str
    sources: Optional[list[str]] = None  # Source documents used for RAG
    tool_calls: Optional[list[ToolCall]] = None  # Tools that were executed
