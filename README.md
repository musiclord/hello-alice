# 🤖 Alice - AI Assistant with Memory

Alice is an advanced AI chatbot built with **Clean Architecture** principles, featuring memory capabilities and conversation management. The system uses Hugging Face Transformers for natural language processing and follows SOTA (State-of-the-Art) design patterns.

## 🏗️ Architecture

This project follows **Clean Architecture** (Robert C. Martin) with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    🎯 Application Layer                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Controllers   │  │   Presenters    │  │  Adapters    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    💼 Use Cases Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Chatbot Logic  │  │  Memory Logic   │  │ Model Mgmt   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    🎭 Domain Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │    Entities     │  │   Abstracts     │  │    Models    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                  🔧 Infrastructure Layer                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Hugging Face    │  │ File Storage    │  │  External    │ │
│  │ Transformers    │  │  Repository     │  │   Services   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Features

### Core Capabilities
- 🧠 **Memory Management**: Remembers important information like object locations, dates, and personal details
- 💬 **Contextual Conversations**: Maintains conversation history and context
- 🔄 **Multiple Model Support**: Works with various Hugging Face models
- 📝 **Conversation Analytics**: Analyzes conversation patterns and topics
- 🎯 **Clean Architecture**: Maintainable, testable, and scalable design

### Memory Examples
- 💼 **Object Tracking**: "My wallet is at the main desk" → Remembers wallet location
- 🔑 **Key Locations**: "Car keys hang at the wall rack beside door" → Stores key location  
- 📅 **Important Dates**: "Mr.A birthday is coming in 4 days (2001/06/19)" → Remembers birthdays
- 🏠 **Personal Info**: Stores and retrieves personal preferences and information

### Technical Features
- **Async/Await**: Modern asynchronous programming
- **Type Hints**: Full type annotation for better code quality
- **Rich CLI**: Beautiful console interface with colors and formatting
- **Extensible**: Easy to add new features and models
- **Testable**: Comprehensive test suite with mocking

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd hello-alice
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run Alice**:
```bash
python main.py
```

### First Conversation

```
🤖 Alice: Hello! I'm Alice, your AI assistant with memory capabilities.

💬 You: My car keys are on the kitchen counter
🤖 Alice: Got it! I'll remember that your car keys are on the kitchen counter. 

💬 You: Where did I put my car keys?
🤖 Alice: Based on what I remember:
📝 - car keys: kitchen counter

Your car keys are on the kitchen counter!
```

## 💻 Usage

### Commands
- **Chat normally**: Just type your message
- `/memory <key> <value>` - Store a memory item
- `/history` - View conversation history  
- `/new` - Start a new conversation
- `/models` - List available models
- `/quit` - Exit the application

### Model Configuration

Alice supports multiple models:
- `distilgpt2` - Lightweight, fast (recommended for testing)
- `dialogpt-medium` - Better conversation quality
- `gpt2` - General purpose model

## 🏛️ Project Structure

```
hello-alice/
├── agent/                          # Core application
│   ├── entities.py                 # Domain entities & abstractions
│   ├── use_cases.py               # Business logic layer
│   ├── adapters.py                # Interface adapters
│   ├── features.py                # Advanced features
│   ├── infrastructure/            # External services
│   │   └── __init__.py           # HuggingFace & storage implementations
│   └── _agent.py                 # Main application class
├── data/                          # Data storage
│   └── conversations/            # JSON conversation files
├── requirements.txt              # Python dependencies
├── config.py                     # Configuration settings
├── main.py                       # Application entry point
├── test_alice.py                 # Test suite
└── README.md                     # This file
```

## 🧪 Testing

Run the test suite:
```bash
python test_alice.py
```

Tests cover:
- ✅ Entity creation and validation
- ✅ Memory extraction algorithms  
- ✅ Conversation analysis
- ✅ Use case logic with mocked dependencies
- ✅ End-to-end workflow

## 🔧 Architecture Details

### Clean Architecture Layers

1. **Entities** (`entities.py`): Core business objects
   - `Message`, `Conversation`, `ModelConfig`
   - Abstract interfaces for `LanguageModel` and `Repository`

2. **Use Cases** (`use_cases.py`): Application business rules
   - `ChatbotUseCase`: Main conversation logic
   - `MemoryUseCase`: Memory management
   - `ModelManagementUseCase`: Model loading/management

3. **Interface Adapters** (`adapters.py`): Convert data for use cases
   - `ChatbotController`: HTTP-like interface
   - `ConsolePresenter`: Rich console output
   - `ConfigurationAdapter`: Settings management

4. **Infrastructure** (`infrastructure/`): External interfaces
   - `HuggingFaceLanguageModel`: Transformers implementation
   - `JSONFileRepository`: File-based storage
   - External service integrations

### Key Principles

- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Interface Segregation**: Clients depend only on methods they use
- **Testability**: Easy mocking and unit testing

## 🚀 Advanced Features

### Memory System
- **Automatic Extraction**: Identifies factual information from conversations
- **Categorization**: Organizes memories by type (location, personal, schedule)
- **Context-Aware Retrieval**: Finds relevant memories based on current conversation
- **Confidence Scoring**: Weights memories by relevance and recency

### Conversation Analytics
- **Topic Detection**: Identifies main conversation themes
- **Sentiment Analysis**: Basic mood detection
- **Pattern Recognition**: Finds conversation patterns and preferences

### Response Enhancement
- **Memory Integration**: Automatically includes relevant memories in responses
- **Helpful Suggestions**: Provides contextual tips and recommendations
- **Rich Formatting**: Uses emojis and formatting for better readability

## 🔮 Future Enhancements

- 🌐 **Web Interface**: React/FastAPI web application
- 🔍 **Vector Search**: Semantic memory search with embeddings
- 🕸️ **Knowledge Graph**: Graph-based memory relationships
- 🌍 **Multi-language**: Support for multiple languages
- 🤝 **API Integration**: External service connections
- 📊 **Analytics Dashboard**: Conversation insights and statistics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow Clean Architecture principles
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Built with ❤️ using Clean Architecture principles and Hugging Face Transformers*