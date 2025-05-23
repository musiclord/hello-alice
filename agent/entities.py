"""
Core domain entities for the chatbot system.
Following Clean Architecture principles.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
from datetime import datetime


class MessageRole(Enum):
    """Message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """Core message entity."""
    id: str
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now()


@dataclass
class Conversation:
    """Conversation entity containing multiple messages."""
    id: str
    messages: List[Message]
    title: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.updated_at:
            self.updated_at = datetime.now()
    
    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_context_messages(self, max_length: int = 10) -> List[Message]:
        """Get recent messages for context."""
        return self.messages[-max_length:]


@dataclass
class ModelConfig:
    """Configuration for the language model."""
    model_name: str
    max_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    do_sample: bool = True
    pad_token_id: Optional[int] = None
    eos_token_id: Optional[int] = None
    device: str = "auto"


@dataclass
class ChatResponse:
    """Response from the chatbot."""
    message: Message
    confidence: Optional[float] = None
    processing_time: Optional[float] = None
    model_info: Optional[Dict[str, Any]] = None


class ChatbotRepository(ABC):
    """Abstract repository for chatbot data persistence."""
    
    @abstractmethod
    async def save_conversation(self, conversation: Conversation) -> None:
        """Save a conversation."""
        pass
    
    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        pass
    
    @abstractmethod
    async def list_conversations(self, limit: int = 50) -> List[Conversation]:
        """List conversations."""
        pass


class LanguageModel(ABC):
    """Abstract interface for language model."""
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[Message], 
        config: ModelConfig
    ) -> ChatResponse:
        """Generate a response given conversation context."""
        pass
    
    @abstractmethod
    async def load_model(self, config: ModelConfig) -> None:
        """Load the language model."""
        pass
    
    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        pass
