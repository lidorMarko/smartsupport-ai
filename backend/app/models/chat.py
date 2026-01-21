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


class ChatResponse(BaseModel):
    message: str
    sources: Optional[list[str]] = None  # Source documents used for RAG
