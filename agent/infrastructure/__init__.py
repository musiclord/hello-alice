"""
Infrastructure layer implementations.
Contains concrete implementations of repositories and external services.
"""
import json
import os
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    GenerationConfig,
    pipeline
)

from ..entities import (
    Message, 
    Conversation, 
    ChatResponse, 
    MessageRole,
    ModelConfig,
    LanguageModel,
    ChatbotRepository
)


class JSONFileRepository(ChatbotRepository):
    """File-based repository using JSON storage."""
    
    def __init__(self, storage_path: str = "data/conversations"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _conversation_to_dict(self, conversation: Conversation) -> Dict[str, Any]:
        """Convert conversation to dictionary."""
        return {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "metadata": conversation.metadata,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata
                }
                for msg in conversation.messages
            ]
        }
    
    def _dict_to_conversation(self, data: Dict[str, Any]) -> Conversation:
        """Convert dictionary to conversation."""
        messages = [
            Message(
                id=msg["id"],
                role=MessageRole(msg["role"]),
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
                metadata=msg.get("metadata")
            )
            for msg in data["messages"]
        ]
        
        return Conversation(
            id=data["id"],
            messages=messages,
            title=data["title"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata")
        )
    
    async def save_conversation(self, conversation: Conversation) -> None:
        """Save conversation to JSON file."""
        file_path = self.storage_path / f"{conversation.id}.json"
        data = self._conversation_to_dict(conversation)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation from JSON file."""
        file_path = self.storage_path / f"{conversation_id}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._dict_to_conversation(data)
        except (json.JSONDecodeError, KeyError):
            return None
    
    async def list_conversations(self, limit: int = 50) -> List[Conversation]:
        """List conversations from JSON files."""
        conversations = []
        
        json_files = list(self.storage_path.glob("*.json"))
        json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for file_path in json_files[:limit]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                conversations.append(self._dict_to_conversation(data))
            except (json.JSONDecodeError, KeyError):
                continue
        
        return conversations


class HuggingFaceLanguageModel(LanguageModel):
    """Hugging Face Transformers implementation."""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.generation_config = None
        self.device = None
        self._loaded = False
    
    async def load_model(self, config: ModelConfig) -> None:
        """Load Hugging Face model."""
        try:
            # Determine device
            if config.device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                self.device = config.device
            
            print(f"Loading model {config.model_name} on {self.device}...")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                config.model_name,
                trust_remote_code=True
            )
            
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                config.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            # Set generation config
            self.generation_config = GenerationConfig(
                max_length=config.max_length,
                temperature=config.temperature,
                top_p=config.top_p,
                do_sample=config.do_sample,
                pad_token_id=config.pad_token_id or self.tokenizer.pad_token_id,
                eos_token_id=config.eos_token_id or self.tokenizer.eos_token_id,
            )
            
            self._loaded = True
            print(f"Model {config.model_name} loaded successfully!")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            self._loaded = False
            raise
    
    def _messages_to_prompt(self, messages: List[Message]) -> str:
        """Convert messages to a single prompt string."""
        prompt_parts = []
        
        for message in messages:
            if message.role == MessageRole.SYSTEM:
                prompt_parts.append(f"System: {message.content}")
            elif message.role == MessageRole.USER:
                prompt_parts.append(f"Human: {message.content}")
            elif message.role == MessageRole.ASSISTANT:
                prompt_parts.append(f"Assistant: {message.content}")
        
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)
    
    async def generate_response(
        self, 
        messages: List[Message], 
        config: ModelConfig
    ) -> ChatResponse:
        """Generate response using Hugging Face model."""
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call load_model first.")
        
        start_time = datetime.now()
        
        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages)
        
        # Tokenize input
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        inputs = inputs.to(self.device)
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                generation_config=self.generation_config,
                max_new_tokens=min(config.max_length, 512),
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        # Decode response
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the new generated part
        response_content = full_response[len(prompt):].strip()
        
        # Clean up response
        if response_content.startswith("Assistant:"):
            response_content = response_content[10:].strip()
        
        # Create response message
        response_message = Message(
            id="",
            role=MessageRole.ASSISTANT,
            content=response_content,
            timestamp=datetime.now()
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ChatResponse(
            message=response_message,
            processing_time=processing_time,
            model_info={
                "model_name": config.model_name,
                "device": self.device,
                "max_length": config.max_length
            }
        )
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._loaded


class HuggingFacePipelineModel(LanguageModel):
    """Alternative implementation using Hugging Face pipeline."""
    
    def __init__(self):
        self.pipeline = None
        self._loaded = False
        self.model_name = None
    
    async def load_model(self, config: ModelConfig) -> None:
        """Load model using Hugging Face pipeline."""
        try:
            device = 0 if torch.cuda.is_available() and config.device != "cpu" else -1
            
            print(f"Loading pipeline for {config.model_name}...")
            
            self.pipeline = pipeline(
                "text-generation",
                model=config.model_name,
                device=device,
                torch_dtype=torch.float16 if device >= 0 else torch.float32,
                trust_remote_code=True
            )
            
            self.model_name = config.model_name
            self._loaded = True
            print(f"Pipeline for {config.model_name} loaded successfully!")
            
        except Exception as e:
            print(f"Error loading pipeline: {e}")
            self._loaded = False
            raise
    
    async def generate_response(
        self, 
        messages: List[Message], 
        config: ModelConfig
    ) -> ChatResponse:
        """Generate response using pipeline."""
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call load_model first.")
        
        start_time = datetime.now()
        
        # Convert messages to conversation format
        conversation = []
        for message in messages:
            if message.role == MessageRole.USER:
                conversation.append({"role": "user", "content": message.content})
            elif message.role == MessageRole.ASSISTANT:
                conversation.append({"role": "assistant", "content": message.content})
            elif message.role == MessageRole.SYSTEM:
                conversation.append({"role": "system", "content": message.content})
        
        # Generate response
        try:
            response = self.pipeline(
                conversation,
                max_new_tokens=min(config.max_length, 512),
                temperature=config.temperature,
                top_p=config.top_p,
                do_sample=config.do_sample,
                return_full_text=False
            )
            
            response_content = response[0]["generated_text"].strip()
            
        except Exception:
            # Fallback to simple text generation
            prompt = self._messages_to_prompt(messages)
            response = self.pipeline(
                prompt,
                max_new_tokens=min(config.max_length, 512),
                temperature=config.temperature,
                top_p=config.top_p,
                do_sample=config.do_sample,
                return_full_text=False
            )
            response_content = response[0]["generated_text"].strip()
        
        # Create response message
        response_message = Message(
            id="",
            role=MessageRole.ASSISTANT,
            content=response_content,
            timestamp=datetime.now()
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ChatResponse(
            message=response_message,
            processing_time=processing_time,
            model_info={
                "model_name": self.model_name,
                "pipeline": True
            }
        )
    
    def _messages_to_prompt(self, messages: List[Message]) -> str:
        """Convert messages to prompt for fallback."""
        prompt_parts = []
        for message in messages:
            if message.role == MessageRole.USER:
                prompt_parts.append(f"User: {message.content}")
            elif message.role == MessageRole.ASSISTANT:
                prompt_parts.append(f"Assistant: {message.content}")
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._loaded
