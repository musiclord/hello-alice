"""
Interface adapters layer.
Contains presenters, controllers, and gateways.
"""
import asyncio
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from datetime import datetime

from .entities import ModelConfig
from .use_cases import ChatbotUseCase, MemoryUseCase, ModelManagementUseCase


class ChatbotController:
    """Controller for chatbot interactions."""
    
    def __init__(
        self, 
        chatbot_use_case: ChatbotUseCase,
        memory_use_case: MemoryUseCase,
        model_management_use_case: ModelManagementUseCase
    ):
        self.chatbot_use_case = chatbot_use_case
        self.memory_use_case = memory_use_case
        self.model_management_use_case = model_management_use_case
        self.current_conversation_id: Optional[str] = None
    
    async def start_new_conversation(self, system_prompt: Optional[str] = None) -> str:
        """Start a new conversation and return conversation ID."""
        conversation = await self.chatbot_use_case.start_conversation(system_prompt)
        self.current_conversation_id = conversation.id
        return conversation.id
    
    async def send_message(
        self, 
        message: str, 
        conversation_id: Optional[str] = None,
        model_config: Optional[ModelConfig] = None
    ) -> Dict[str, Any]:
        """Send a message and return response data."""
        target_conversation_id = conversation_id or self.current_conversation_id
        
        if not target_conversation_id:
            # Start new conversation if none exists
            target_conversation_id = await self.start_new_conversation()
        
        try:
            response = await self.chatbot_use_case.send_message(
                target_conversation_id, 
                message, 
                model_config
            )
            
            return {
                "success": True,
                "response": response.message.content,
                "conversation_id": target_conversation_id,
                "processing_time": response.processing_time,
                "model_info": response.model_info
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "conversation_id": target_conversation_id
            }
    
    async def get_conversation_history(self, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Get conversation history."""
        target_conversation_id = conversation_id or self.current_conversation_id
        
        if not target_conversation_id:
            return {"success": False, "error": "No active conversation"}
        
        try:
            conversation = await self.chatbot_use_case.get_conversation_history(target_conversation_id)
            if not conversation:
                return {"success": False, "error": "Conversation not found"}
            
            return {
                "success": True,
                "conversation": {
                    "id": conversation.id,
                    "title": conversation.title,
                    "created_at": conversation.created_at.isoformat(),
                    "messages": [
                        {
                            "role": msg.role.value,
                            "content": msg.content,
                            "timestamp": msg.timestamp.isoformat()
                        }
                        for msg in conversation.messages
                    ]
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def store_memory(self, key: str, value: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Store a memory item."""
        try:
            await self.memory_use_case.store_memory(key, value, context)
            return {"success": True, "message": f"Memory stored: {key}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def load_model(self, model_config: ModelConfig) -> Dict[str, Any]:
        """Load a language model."""
        try:
            await self.model_management_use_case.load_model(model_config)
            return {"success": True, "message": f"Model {model_config.model_name} loaded successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}


class ConsolePresenter:
    """Console-based presenter for rich output."""
    
    def __init__(self):
        self.console = Console()
    
    def show_welcome(self) -> None:
        """Show welcome message."""
        welcome_text = """
# 🤖 Alice Chatbot

Welcome to Alice, your AI assistant with memory capabilities!

**Available Commands:**
- Just type your message to chat
- `/memory <key> <value>` - Store a memory
- `/history` - View conversation history
- `/new` - Start new conversation
- `/quit` - Exit the application

**Features:**
- 💭 Conversational AI with context awareness
- 🧠 Memory storage for important information
- 📝 Conversation history
- 🔧 Configurable language models
        """
        
        self.console.print(Panel(
            Markdown(welcome_text),
            title="🌟 Alice AI Assistant",
            border_style="blue"
        ))
    
    def show_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Show a message in the console."""
        if role == "user":
            self.console.print(f"[bold blue]You:[/bold blue] {content}")
        elif role == "assistant":
            self.console.print(Panel(
                Markdown(content),
                title="🤖 Alice",
                border_style="green"
            ))
            
            if metadata:
                info_text = f"Processing time: {metadata.get('processing_time', 'N/A'):.2f}s"
                if metadata.get('model_info'):
                    model_name = metadata['model_info'].get('model_name', 'Unknown')
                    info_text += f" | Model: {model_name}"
                self.console.print(f"[dim]{info_text}[/dim]")
        elif role == "system":
            self.console.print(f"[dim yellow]System:[/dim yellow] {content}")
    
    def show_error(self, error: str) -> None:
        """Show an error message."""
        self.console.print(Panel(
            f"[red]Error: {error}[/red]",
            title="❌ Error",
            border_style="red"
        ))
    
    def show_success(self, message: str) -> None:
        """Show a success message."""
        self.console.print(f"[green]✅ {message}[/green]")
    
    def show_info(self, message: str) -> None:
        """Show an info message."""
        self.console.print(f"[blue]ℹ️  {message}[/blue]")
    
    def show_conversation_history(self, conversation_data: Dict[str, Any]) -> None:
        """Show conversation history."""
        conversation = conversation_data["conversation"]
        
        table = Table(title=f"Conversation: {conversation['title']}")
        table.add_column("Time", style="dim")
        table.add_column("Role", style="bold")
        table.add_column("Message")
        
        for msg in conversation["messages"]:
            timestamp = datetime.fromisoformat(msg["timestamp"])
            table.add_row(
                timestamp.strftime("%H:%M:%S"),
                msg["role"].title(),
                msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            )
        
        self.console.print(table)
    
    def show_loading(self, message: str) -> None:
        """Show loading message."""
        self.console.print(f"[yellow]⏳ {message}[/yellow]")


class ConfigurationAdapter:
    """Adapter for configuration management."""
    
    @staticmethod
    def get_default_model_config() -> ModelConfig:
        """Get default model configuration."""
        return ModelConfig(
            model_name="microsoft/DialoGPT-medium",  # Good for conversation
            max_length=512,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            device="auto"
        )
    
    @staticmethod
    def get_model_configs() -> Dict[str, ModelConfig]:
        """Get predefined model configurations."""
        return {
            "dialogpt-small": ModelConfig(
                model_name="microsoft/DialoGPT-small",
                max_length=256,
                temperature=0.8,
                device="auto"
            ),
            "dialogpt-medium": ModelConfig(
                model_name="microsoft/DialoGPT-medium",
                max_length=512,
                temperature=0.7,
                device="auto"
            ),
            "gpt2": ModelConfig(
                model_name="gpt2",
                max_length=512,
                temperature=0.7,
                device="auto"
            ),
            "distilgpt2": ModelConfig(
                model_name="distilgpt2",
                max_length=256,
                temperature=0.8,
                device="auto"
            )
        }
    
    @staticmethod
    def get_system_prompts() -> Dict[str, str]:
        """Get predefined system prompts."""
        return {
            "assistant": "You are Alice, a helpful AI assistant. You are friendly, knowledgeable, and always try to be helpful. You can remember things that users tell you.",
            "casual": "You are Alice, a casual and friendly AI companion. Keep conversations light and engaging.",
            "professional": "You are Alice, a professional AI assistant. Provide clear, concise, and accurate information.",
            "creative": "You are Alice, a creative AI assistant. Help users with creative tasks, brainstorming, and innovative solutions."
        }
