# Alice Chatbot Configuration Examples

# Model configurations for different use cases
MODEL_CONFIGS = {
    # Lightweight models for testing
    "distilgpt2": {
        "model_name": "distilgpt2",
        "max_length": 256,
        "temperature": 0.8
    },
    
    # Conversation-optimized models
    "dialogpt-small": {
        "model_name": "microsoft/DialoGPT-small", 
        "max_length": 256,
        "temperature": 0.8
    },
    "dialogpt-medium": {
        "model_name": "microsoft/DialoGPT-medium",
        "max_length": 512, 
        "temperature": 0.7
    },
    
    # General purpose models
    "gpt2": {
        "model_name": "gpt2",
        "max_length": 512,
        "temperature": 0.7
    },
    
    # For Chinese language support (if needed)
    "gpt2-chinese": {
        "model_name": "uer/gpt2-chinese-cluecorpussmall",
        "max_length": 256,
        "temperature": 0.8
    }
}

# System prompts for different personalities
SYSTEM_PROMPTS = {
    "assistant": "You are Alice, a helpful AI assistant. You are friendly, knowledgeable, and always try to be helpful. You can remember things that users tell you.",
    "casual": "You are Alice, a casual and friendly AI companion. Keep conversations light and engaging.",
    "professional": "You are Alice, a professional AI assistant. Provide clear, concise, and accurate information.",
    "creative": "You are Alice, a creative AI assistant. Help users with creative tasks, brainstorming, and innovative solutions.",
    "memory_focused": "You are Alice, an AI assistant with excellent memory. You remember everything users tell you and can recall information when needed. You help users keep track of important things like where they put items, important dates, and personal information."
}

# Default settings
DEFAULT_MODEL = "distilgpt2"  # Start with lightweight model
DEFAULT_PERSONALITY = "memory_focused"
DATA_PATH = "data/conversations"
