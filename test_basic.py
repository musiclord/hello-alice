"""
簡化版測試套件 - 測試 Alice Chatbot 的核心功能
"""
import sys
import os
from datetime import datetime

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 導入核心實體
from agent.entities import Message, Conversation, MessageRole, ModelConfig, ChatResponse


def test_message_creation():
    """測試訊息實體創建"""
    print("🧪 測試訊息創建...")
    
    message = Message(
        id="",
        role=MessageRole.USER,
        content="Hello, Alice!",
        timestamp=datetime.now()
    )
    
    assert message.role == MessageRole.USER
    assert message.content == "Hello, Alice!"
    assert message.id  # 應該自動生成 ID
    print("✅ 訊息創建測試通過")


def test_conversation_creation():
    """測試對話實體創建"""
    print("🧪 測試對話創建...")
    
    conversation = Conversation(
        id="",
        messages=[]
    )
    
    assert conversation.id  # 應該自動生成 ID
    assert len(conversation.messages) == 0
    
    # 測試添加訊息
    message = Message("", MessageRole.USER, "Test", datetime.now())
    conversation.add_message(message)
    
    assert len(conversation.messages) == 1
    assert conversation.messages[0] == message
    print("✅ 對話創建測試通過")


def test_model_config():
    """測試模型配置"""
    print("🧪 測試模型配置...")
    
    config = ModelConfig(
        model_name="test-model",
        max_length=512,
        temperature=0.7,
        top_p=0.9
    )
    
    assert config.model_name == "test-model"
    assert config.max_length == 512
    assert config.temperature == 0.7
    print("✅ 模型配置測試通過")


def test_chat_response():
    """測試聊天回應"""
    print("🧪 測試聊天回應...")
    
    message = Message("", MessageRole.ASSISTANT, "Hello there!", datetime.now())
    response = ChatResponse(
        message=message,
        processing_time=0.1,
        confidence=0.95
    )
    
    assert response.message.content == "Hello there!"
    assert response.processing_time == 0.1
    assert response.confidence == 0.95
    print("✅ 聊天回應測試通過")


def test_message_roles():
    """測試訊息角色枚舉"""
    print("🧪 測試訊息角色...")
    
    assert MessageRole.USER.value == "user"
    assert MessageRole.ASSISTANT.value == "assistant"
    assert MessageRole.SYSTEM.value == "system"
    print("✅ 訊息角色測試通過")


def test_conversation_context():
    """測試對話上下文管理"""
    print("🧪 測試對話上下文...")
    
    conversation = Conversation("test", [])
    
    # 添加多個訊息
    for i in range(15):
        message = Message("", MessageRole.USER, f"Message {i}", datetime.now())
        conversation.add_message(message)
    
    # 測試獲取上下文訊息
    context = conversation.get_context_messages(max_length=10)
    assert len(context) == 10
    assert context[-1].content == "Message 14"  # 最後一個訊息
    print("✅ 對話上下文測試通過")


def run_basic_tests():
    """運行基本測試"""
    print("🚀 開始運行 Alice Chatbot 基本測試...")
    print("=" * 50)
    
    try:
        test_message_creation()
        test_conversation_creation()
        test_model_config()
        test_chat_response()
        test_message_roles()
        test_conversation_context()
        
        print("=" * 50)
        print("🎉 所有基本測試通過！")
        print("\n📋 測試摘要:")
        print("✅ 訊息實體測試")
        print("✅ 對話實體測試") 
        print("✅ 模型配置測試")
        print("✅ 聊天回應測試")
        print("✅ 訊息角色測試")
        print("✅ 對話上下文測試")
        
        print("\n💡 接下來您可以:")
        print("1. 安裝完整依賴: pip install torch transformers")
        print("2. 運行完整系統: python main.py")
        print("3. 測試記憶功能和模型集成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)
