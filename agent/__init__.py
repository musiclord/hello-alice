"""
Main package initialization for Alice Chatbot agent.
"""
from .entities import Message, Conversation, MessageRole, ModelConfig, ChatResponse

__all__ = [
    "Message",
    "Conversation", 
    "MessageRole",
    "ModelConfig",
    "ChatResponse"
]

__version__ = "1.0.0"