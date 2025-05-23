"""
Alice Chatbot - Main Application Entry Point
Following Clean Architecture principles for a maintainable and scalable chatbot.
"""
import asyncio
import os
from typing import Optional

from .entities import ModelConfig
from .use_cases import ChatbotUseCase, MemoryUseCase, ModelManagementUseCase
from .infrastructure import JSONFileRepository, HuggingFaceLanguageModel, HuggingFacePipelineModel
from .adapters import ChatbotController, ConsolePresenter, ConfigurationAdapter


class AliceChatbot:
    """Main Alice Chatbot application."""
    
    def __init__(self, use_pipeline: bool = True):
        """Initialize the chatbot with dependency injection."""
        # Infrastructure layer
        self.repository = JSONFileRepository()
        
        # Choose model implementation
        if use_pipeline:
            self.language_model = HuggingFacePipelineModel()
        else:
            self.language_model = HuggingFaceLanguageModel()
        
        # Use case layer
        self.chatbot_use_case = ChatbotUseCase(
            self.language_model,
            self.repository,
            ConfigurationAdapter.get_default_model_config()
        )
        self.memory_use_case = MemoryUseCase(self.repository)
        self.model_management_use_case = ModelManagementUseCase(self.language_model)
        
        # Interface adapter layer
        self.controller = ChatbotController(
            self.chatbot_use_case,
            self.memory_use_case,
            self.model_management_use_case
        )
        self.presenter = ConsolePresenter()
    
    async def initialize(self, model_name: Optional[str] = None) -> None:
        """Initialize the chatbot and load model."""
        self.presenter.show_welcome()
        
        # Load model
        if model_name:
            configs = ConfigurationAdapter.get_model_configs()
            if model_name in configs:
                config = configs[model_name]
            else:
                config = ModelConfig(model_name=model_name)
        else:
            config = ConfigurationAdapter.get_default_model_config()
        
        self.presenter.show_loading(f"Loading model: {config.model_name}")
        
        result = await self.controller.load_model(config)
        if result["success"]:
            self.presenter.show_success(result["message"])
        else:
            self.presenter.show_error(result["error"])
            return
        
        # Start conversation with system prompt
        system_prompts = ConfigurationAdapter.get_system_prompts()
        conversation_id = await self.controller.start_new_conversation(
            system_prompts["assistant"]
        )
        self.presenter.show_info(f"New conversation started: {conversation_id}")
    
    async def run_console_interface(self) -> None:
        """Run the console-based chat interface."""
        try:
            while True:
                # Get user input
                try:
                    user_input = input("\n💬 You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    await self._handle_command(user_input)
                    continue
                
                # Send message
                self.presenter.show_loading("Generating response...")
                result = await self.controller.send_message(user_input)
                
                if result["success"]:
                    self.presenter.show_message(
                        "assistant", 
                        result["response"],
                        {
                            "processing_time": result.get("processing_time"),
                            "model_info": result.get("model_info")
                        }
                    )
                else:
                    self.presenter.show_error(result["error"])
        
        except KeyboardInterrupt:
            pass
        finally:
            self.presenter.show_info("Goodbye! 👋")
    
    async def _handle_command(self, command: str) -> None:
        """Handle special commands."""
        parts = command[1:].split(maxsplit=2)
        cmd = parts[0].lower()
        
        if cmd == "quit" or cmd == "exit":
            raise KeyboardInterrupt
        
        elif cmd == "new":
            conversation_id = await self.controller.start_new_conversation()
            self.presenter.show_success(f"New conversation started: {conversation_id}")
        
        elif cmd == "history":
            result = await self.controller.get_conversation_history()
            if result["success"]:
                self.presenter.show_conversation_history(result)
            else:
                self.presenter.show_error(result["error"])
        
        elif cmd == "memory":
            if len(parts) >= 3:
                key = parts[1]
                value = parts[2]
                result = await self.controller.store_memory(key, value)
                if result["success"]:
                    self.presenter.show_success(result["message"])
                else:
                    self.presenter.show_error(result["error"])
            else:
                self.presenter.show_error("Usage: /memory <key> <value>")
        
        elif cmd == "models":
            configs = ConfigurationAdapter.get_model_configs()
            self.presenter.show_info("Available models:")
            for name in configs.keys():
                self.presenter.show_info(f"  - {name}")
        
        elif cmd == "help":
            self.presenter.show_welcome()
        
        else:
            self.presenter.show_error(f"Unknown command: /{cmd}")


async def main():
    """Main entry point."""
    # Create and run chatbot
    chatbot = AliceChatbot(use_pipeline=True)
    
    try:
        await chatbot.initialize()
        await chatbot.run_console_interface()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())