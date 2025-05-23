"""
Use cases (business logic) for the chatbot system.
This layer contains application-specific business rules.
"""
from typing import List, Optional
import time
from datetime import datetime

from .entities import (
    Message, 
    Conversation, 
    ChatResponse, 
    MessageRole,
    ModelConfig,
    LanguageModel,
    ChatbotRepository
)


class ChatbotUseCase:
    """Main use case for chatbot interactions."""
    
    def __init__(
        self, 
        language_model: LanguageModel,
        repository: ChatbotRepository,
        default_config: ModelConfig
    ):
        self.language_model = language_model
        self.repository = repository
        self.default_config = default_config
    
    async def start_conversation(self, system_prompt: Optional[str] = None) -> Conversation:
        """Start a new conversation."""
        conversation = Conversation(
            id="",  # Will be auto-generated
            messages=[],
            title="New Conversation"
        )
        
        if system_prompt:
            system_message = Message(
                id="",
                role=MessageRole.SYSTEM,
                content=system_prompt,
                timestamp=datetime.now()
            )
            conversation.add_message(system_message)
        
        await self.repository.save_conversation(conversation)
        return conversation
    
    async def send_message(
        self, 
        conversation_id: str, 
        user_message: str,
        config: Optional[ModelConfig] = None
    ) -> ChatResponse:
        """Send a message and get response."""
        start_time = time.time()
        
        # Get conversation
        conversation = await self.repository.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Add user message
        user_msg = Message(
            id="",
            role=MessageRole.USER,
            content=user_message,
            timestamp=datetime.now()
        )
        conversation.add_message(user_msg)
        
        # Ensure model is loaded
        model_config = config or self.default_config
        if not self.language_model.is_loaded():
            await self.language_model.load_model(model_config)
        
        # Get context messages for generation
        context_messages = conversation.get_context_messages()
        
        # Generate response
        response = await self.language_model.generate_response(
            context_messages, 
            model_config
        )
        
        # Add processing time
        response.processing_time = time.time() - start_time
        
        # Add assistant message to conversation
        conversation.add_message(response.message)
        
        # Save updated conversation
        await self.repository.save_conversation(conversation)
        
        return response
    
    async def get_conversation_history(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation history."""
        return await self.repository.get_conversation(conversation_id)
    
    async def list_conversations(self, limit: int = 50) -> List[Conversation]:
        """List all conversations."""
        return await self.repository.list_conversations(limit)


class MemoryUseCase:
    """Use case for managing chatbot memory and knowledge."""
    
    def __init__(self, repository: ChatbotRepository):
        self.repository = repository
    
    async def store_memory(self, key: str, value: str, context: Optional[str] = None) -> None:
        """Store a memory item."""
        # This could be extended to use a knowledge graph or vector database
        memory_conversation = Conversation(
            id=f"memory_{key}",
            messages=[
                Message(
                    id="",
                    role=MessageRole.SYSTEM,
                    content=f"MEMORY: {key} = {value}",
                    timestamp=datetime.now(),
                    metadata={"type": "memory", "key": key, "context": context}
                )
            ],
            title=f"Memory: {key}",
            metadata={"type": "memory"}
        )
        await self.repository.save_conversation(memory_conversation)
    
    async def retrieve_memories(self, query: str) -> List[str]:
        """Retrieve relevant memories based on query."""
        # This is a simplified implementation
        # In a real system, you'd use vector similarity or knowledge graph queries
        conversations = await self.repository.list_conversations()
        memories = []
        
        for conv in conversations:
            if conv.metadata and conv.metadata.get("type") == "memory":
                for message in conv.messages:
                    if message.metadata and message.metadata.get("type") == "memory":
                        if query.lower() in message.content.lower():
                            memories.append(message.content)
        
        return memories


class ModelManagementUseCase:
    """Use case for managing language models."""
    
    def __init__(self, language_model: LanguageModel):
        self.language_model = language_model
    
    async def load_model(self, config: ModelConfig) -> None:
        """Load a language model."""
        await self.language_model.load_model(config)
    
    def get_model_status(self) -> bool:
        """Get model loading status."""
        return self.language_model.is_loaded()
