"""
Alice Chatbot 集成測試 - 測試實際的 HuggingFace 模型
"""
import asyncio
import os
import sys
from typing import Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent._agent import AliceChatbot
from agent.entities import ModelConfig
from agent.adapters import ConfigurationAdapter


class TestPresenter:
    """測試用的簡化輸出器"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def log(self, message: str):
        if self.verbose:
            print(f"🔍 {message}")
    
    def success(self, message: str):
        print(f"✅ {message}")
    
    def error(self, message: str):
        print(f"❌ {message}")


async def test_model_loading():
    """測試模型載入功能"""
    presenter = TestPresenter()
    presenter.log("測試模型載入...")
    
    try:
        # 使用輕量級模型進行測試
        chatbot = AliceChatbot(use_pipeline=True)
        
        # 手動初始化以避免互動式介面
        presenter.log("初始化聊天機器人...")
        
        # 使用更小的模型進行測試
        test_config = ModelConfig(
            model_name="microsoft/DialoGPT-small",
            max_length=100,
            temperature=0.7,
            do_sample=True
        )
        
        presenter.log(f"載入模型: {test_config.model_name}")
        result = await chatbot.controller.load_model(test_config)
        
        if result["success"]:
            presenter.success(f"模型載入成功: {result['message']}")
            return chatbot
        else:
            presenter.error(f"模型載入失敗: {result['error']}")
            return None
            
    except Exception as e:
        presenter.error(f"模型載入過程出錯: {str(e)}")
        return None


async def test_conversation_flow(chatbot: AliceChatbot):
    """測試對話流程"""
    presenter = TestPresenter()
    presenter.log("測試對話流程...")
    
    try:
        # 開始新對話
        conversation_id = await chatbot.controller.start_new_conversation(
            "You are Alice, a helpful AI assistant."
        )
        presenter.success(f"對話開始: {conversation_id}")
        
        # 測試訊息
        test_messages = [
            "Hello, how are you?",
            "What is your name?",
            "Can you help me with something?"
        ]
        
        for i, message in enumerate(test_messages, 1):
            presenter.log(f"發送測試訊息 {i}: {message}")
            
            result = await chatbot.controller.send_message(message)
            
            if result["success"]:
                presenter.success(f"回應 {i}: {result['response'][:100]}...")
                if result.get("processing_time"):
                    presenter.log(f"處理時間: {result['processing_time']:.2f}秒")
            else:
                presenter.error(f"訊息 {i} 發送失敗: {result['error']}")
                return False
        
        return True
        
    except Exception as e:
        presenter.error(f"對話測試出錯: {str(e)}")
        return False


async def test_memory_functionality(chatbot: AliceChatbot):
    """測試記憶功能"""
    presenter = TestPresenter()
    presenter.log("測試記憶功能...")
    
    try:
        # 測試記憶儲存
        test_memories = [
            ("wallet_location", "on the kitchen table"),
            ("car_keys", "hanging by the front door"),
            ("birthday", "June 19th, 2001")
        ]
        
        for key, value in test_memories:
            result = await chatbot.controller.store_memory(key, value)
            if result["success"]:
                presenter.success(f"記憶儲存成功: {key} = {value}")
            else:
                presenter.error(f"記憶儲存失敗: {result['error']}")
                return False
        
        # 測試記憶檢索
        presenter.log("測試記憶檢索...")
        memory_result = await chatbot.controller.get_memories()
        
        if memory_result["success"]:
            memories = memory_result["memories"]
            presenter.success(f"檢索到 {len(memories)} 條記憶")
            for key, value in memories.items():
                presenter.log(f"  {key}: {value}")
        else:
            presenter.error(f"記憶檢索失敗: {memory_result['error']}")
            return False
        
        return True
        
    except Exception as e:
        presenter.error(f"記憶測試出錯: {str(e)}")
        return False


async def test_conversation_history(chatbot: AliceChatbot):
    """測試對話歷史功能"""
    presenter = TestPresenter()
    presenter.log("測試對話歷史...")
    
    try:
        result = await chatbot.controller.get_conversation_history()
        
        if result["success"]:
            conversation = result["conversation"]
            messages = conversation.messages
            presenter.success(f"對話歷史包含 {len(messages)} 條訊息")
            
            # 顯示最近幾條訊息
            for message in messages[-3:]:
                presenter.log(f"  {message.role}: {message.content[:50]}...")
        else:
            presenter.error(f"對話歷史檢索失敗: {result['error']}")
            return False
        
        return True
        
    except Exception as e:
        presenter.error(f"對話歷史測試出錯: {str(e)}")
        return False


async def run_comprehensive_test():
    """運行完整的集成測試"""
    print("🚀 開始 Alice Chatbot 集成測試")
    print("=" * 60)
    
    # 測試模型載入
    chatbot = await test_model_loading()
    if not chatbot:
        print("❌ 模型載入失敗，停止測試")
        return False
    
    # 測試對話流程
    if not await test_conversation_flow(chatbot):
        print("❌ 對話流程測試失敗")
        return False
    
    # 測試記憶功能
    if not await test_memory_functionality(chatbot):
        print("❌ 記憶功能測試失敗")
        return False
    
    # 測試對話歷史
    if not await test_conversation_history(chatbot):
        print("❌ 對話歷史測試失敗")
        return False
    
    print("=" * 60)
    print("🎉 所有集成測試通過！")
    print("💡 Alice Chatbot 已準備就緒，可以開始使用")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(run_comprehensive_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 測試被中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 測試過程出錯: {str(e)}")
        sys.exit(1)
