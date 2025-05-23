"""
Simple CLI runner for Alice Chatbot
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent._agent import AliceChatbot


async def main():
    """Main entry point for CLI."""
    print("🚀 Starting Alice Chatbot...")
    
    # Create and run chatbot
    chatbot = AliceChatbot(use_pipeline=True)
    
    try:
        await chatbot.initialize()
        await chatbot.run_console_interface()
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
