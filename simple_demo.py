"""
Alice Chatbot 簡單演示 - 展示 Clean Architecture
"""
import asyncio
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from agent.entities import (
    Message, Conversation, MessageRole, ModelConfig, 
    ChatResponse, LanguageModel, ChatbotRepository
)


class SimplePresenter:
    """簡單的控制台輸出"""
    
    def show_welcome(self):
        print("=" * 60)
        print("🤖 Alice AI 助手 - Clean Architecture 演示")
        print("=" * 60)
        print("功能特色:")
        print("• 🧠 記憶管理 - 記住重要信息")
        print("• 💬 對話管理 - 保持上下文")
        print("• 🏗️ 乾淨架構 - 分層設計")
        print("• 📝 對話歷史 - 完整記錄")
        print()
        print("指令說明:")
        print("• 直接輸入訊息進行對話")
        print("• /memory <鍵> <值> - 儲存記憶")
        print("• /history - 查看對話歷史")
        print("• /quit - 退出程式")
        print("=" * 60)
    
    def show_message(self, role: str, content: str, metadata=None):
        if role == "user":
            print(f"\n👤 您: {content}")
        elif role == "assistant":
            print(f"\n🤖 Alice: {content}")
            if metadata and metadata.get('processing_time'):
                print(f"   ⏱️ 處理時間: {metadata['processing_time']:.2f}秒")
        elif role == "system":
            print(f"\n🔧 系統: {content}")
    
    def show_error(self, error: str):
        print(f"\n❌ 錯誤: {error}")
    
    def show_success(self, message: str):
        print(f"\n✅ {message}")
    
    def show_info(self, message: str):
        print(f"\nℹ️ {message}")
    
    def show_loading(self, message: str):
        print(f"\n⏳ {message}")


class MockLanguageModel(LanguageModel):
    """模擬語言模型"""
    
    def __init__(self):
        self._loaded = False
        self.knowledge_base = {
            "greetings": ["你好", "hello", "hi", "嗨"],
            "memory_keywords": ["記住", "記得", "在哪", "位置", "放在"],
            "gratitude": ["謝謝", "感謝", "thank"],
            "farewell": ["再見", "bye", "goodbye"]
        }
    
    async def load_model(self, config: ModelConfig) -> None:
        await asyncio.sleep(0.5)
        self._loaded = True
    
    def is_loaded(self) -> bool:
        return self._loaded
    
    async def generate_response(self, messages: List[Message], config: ModelConfig) -> ChatResponse:
        await asyncio.sleep(0.2)
        
        if not messages:
            content = "您好！我是 Alice，您的 AI 助手。我可以記住重要信息並協助您管理日常事務。"
        else:
            last_message = messages[-1]
            content = self._generate_smart_response(last_message.content, messages)
        
        response_message = Message(
            id="",
            role=MessageRole.ASSISTANT,
            content=content,
            timestamp=datetime.now()
        )
        
        return ChatResponse(
            message=response_message,
            processing_time=0.2,
            model_info={"model": "Alice-Demo"}
        )
    
    def _generate_smart_response(self, user_input: str, messages: List[Message]) -> str:
        """生成智能回應"""
        user_lower = user_input.lower()
        
        # 問候語
        if any(greeting in user_lower for greeting in self.knowledge_base["greetings"]):
            return "您好！很高興見到您。我是 Alice，您的智能助手。有什麼可以幫您記住或處理的事情嗎？"
        
        # 感謝
        if any(thanks in user_lower for thanks in self.knowledge_base["gratitude"]):
            return "不客氣！很高興能幫助您。如果還有其他需要記住的重要信息，隨時告訴我。"
        
        # 告別
        if any(bye in user_lower for bye in self.knowledge_base["farewell"]):
            return "再見！我會記住我們今天談到的所有重要信息。下次見面時，我還會記得的！"
        
        # 記憶相關
        memory_pattern = re.search(r"(.+?)(?:在|放在|位於)(.+)", user_input)
        if memory_pattern:
            item = memory_pattern.group(1).strip()
            location = memory_pattern.group(2).strip()
            return f"我記住了！{item}在{location}。這個信息我會牢牢記住，下次您詢問時我會告訴您。"
        
        # 查詢位置
        if "在哪" in user_input or "哪裡" in user_input:
            return "請告訴我您想查詢什麼物品的位置？如果您之前告訴過我，我會努力回憶。"
        
        # 默認回應
        return "我理解您的意思。作為您的助手，我會盡力幫助您。如果有重要信息需要記住，請告訴我詳細內容。"


class InMemoryRepository(ChatbotRepository):
    """記憶體儲存庫"""
    
    def __init__(self):
        self.conversations = {}
    
    async def save_conversation(self, conversation: Conversation) -> None:
        self.conversations[conversation.id] = conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return self.conversations.get(conversation_id)
    
    async def list_conversations(self, limit: int = 50) -> List[Conversation]:
        return list(self.conversations.values())[:limit]


class SimpleChatbot:
    """簡化版聊天機器人"""
    
    def __init__(self):
        self.repository = InMemoryRepository()
        self.language_model = MockLanguageModel()
        self.presenter = SimplePresenter()
        self.current_conversation_id = None
        self.memories = {}
    
    async def initialize(self):
        """初始化"""
        self.presenter.show_welcome()
        
        self.presenter.show_loading("正在初始化 Alice...")
        await self.language_model.load_model(ModelConfig("Alice-Demo"))
        self.presenter.show_success("Alice 初始化完成！")
        
        # 建立新對話
        conversation = Conversation(id="", messages=[])
        system_msg = Message(
            id="", role=MessageRole.SYSTEM,
            content="You are Alice, a helpful AI assistant with memory capabilities.",
            timestamp=datetime.now()
        )
        conversation.add_message(system_msg)
        await self.repository.save_conversation(conversation)
        self.current_conversation_id = conversation.id
        
        self.presenter.show_info("新對話已開始！")
    
    async def run(self):
        """運行聊天機器人"""
        try:
            while True:
                try:
                    user_input = input("\n💬 您: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                
                if not user_input:
                    continue
                
                # 處理指令
                if user_input.startswith("/"):
                    await self._handle_command(user_input)
                    continue
                
                # 處理對話
                await self._handle_message(user_input)
        
        except KeyboardInterrupt:
            pass
        finally:
            self.presenter.show_info("謝謝使用 Alice！再見！👋")
    
    async def _handle_message(self, user_input: str):
        """處理用戶訊息"""
        # 取得對話
        conversation = await self.repository.get_conversation(self.current_conversation_id)
        
        # 加入用戶訊息
        user_msg = Message(
            id="", role=MessageRole.USER,
            content=user_input, timestamp=datetime.now()
        )
        conversation.add_message(user_msg)
        
        # 生成回應
        self.presenter.show_loading("正在思考...")
        response = await self.language_model.generate_response(
            conversation.get_context_messages(),
            ModelConfig("Alice-Demo")
        )
        
        # 加入助手回應
        conversation.add_message(response.message)
        await self.repository.save_conversation(conversation)
        
        # 顯示回應
        self.presenter.show_message(
            "assistant", 
            response.message.content,
            {"processing_time": response.processing_time}
        )
    
    async def _handle_command(self, command: str):
        """處理指令"""
        parts = command[1:].split(maxsplit=2)
        cmd = parts[0].lower()
        
        if cmd in ["quit", "exit"]:
            raise KeyboardInterrupt
        
        elif cmd == "memory":
            if len(parts) >= 3:
                key, value = parts[1], parts[2]
                self.memories[key] = value
                self.presenter.show_success(f"已記住: {key} = {value}")
            else:
                self.presenter.show_error("用法: /memory <鍵> <值>")
        
        elif cmd == "history":
            conversation = await self.repository.get_conversation(self.current_conversation_id)
            if conversation:
                print("\n📜 對話歷史:")
                for i, msg in enumerate(conversation.messages[1:], 1):  # 跳過系統訊息
                    role = "您" if msg.role == MessageRole.USER else "Alice"
                    print(f"{i}. {role}: {msg.content}")
            else:
                self.presenter.show_error("找不到對話歷史")
        
        elif cmd == "memories":
            if self.memories:
                print("\n🧠 儲存的記憶:")
                for key, value in self.memories.items():
                    print(f"• {key}: {value}")
            else:
                self.presenter.show_info("目前沒有儲存的記憶")
        
        elif cmd == "help":
            self.presenter.show_welcome()
        
        else:
            self.presenter.show_error(f"未知指令: /{cmd}")


async def main():
    """主函數"""
    print("🚀 啟動 Alice Chatbot 簡單演示...")
    
    chatbot = SimpleChatbot()
    
    try:
        await chatbot.initialize()
        await chatbot.run()
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
