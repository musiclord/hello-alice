"""
Alice Chatbot 演示版本 - 無需 PyTorch
使用模擬語言模型來展示架構和功能
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
from agent.use_cases import ChatbotUseCase, MemoryUseCase
from agent.adapters import ChatbotController, ConsolePresenter, ConfigurationAdapter


class MockLanguageModel(LanguageModel):
    """模擬語言模型，用於演示架構"""
    
    def __init__(self):
        self._loaded = False
        self.responses = {
            # 記憶相關回應
            "wallet": "我記住了！您的錢包在主桌上。這是個很好的固定位置。",
            "keys": "明白了！車鑰匙掛在門旁的牆架上，這樣就不容易忘記了。",
            "birthday": "我會記住這個重要日期！Mr.A 的生日是 2001/06/19，還有 4 天就到了。",
            
            # 一般對話回應
            "hello": "您好！我是 Alice，您的 AI 助手。我可以幫您記住重要的事情，比如物品位置、重要日期等。",
            "how are you": "我很好，謝謝您的關心！我隨時準備幫助您管理和記憶重要信息。",
            "thank": "不客氣！很高興能幫助您。如果您需要我記住什麼重要信息，隨時告訴我。",
            "goodbye": "再見！記住，我會保存我們的對話和您提到的重要信息。下次見面時我還會記得的！",
            
            # 功能介紹
            "help": """我可以幫您做這些事情：
🧠 記憶管理 - 記住物品位置、重要日期、個人信息
💬 對話聊天 - 保持上下文的自然對話
📝 信息查詢 - 快速找到之前提到的信息
📊 對話分析 - 了解對話模式和主題

試試對我說：「我的錢包在書桌上」或「幫我記住明天有會議」"""
        }
    
    async def load_model(self, config: ModelConfig) -> None:
        """模擬載入模型"""
        await asyncio.sleep(0.5)  # 模擬載入時間
        self._loaded = True
    
    def is_loaded(self) -> bool:
        """檢查模型是否已載入"""
        return self._loaded
    
    async def generate_response(
        self, 
        messages: List[Message], 
        config: ModelConfig
    ) -> ChatResponse:
        """生成模擬回應"""
        await asyncio.sleep(0.2)  # 模擬處理時間
        
        if not messages:
            content = "您好！我是 Alice，請問有什麼可以幫您的嗎？"
        else:
            last_message = messages[-1]
            user_input = last_message.content.lower()
            
            # 匹配預定回應
            content = self._generate_smart_response(user_input, messages)
        
        response_message = Message(
            id="",
            role=MessageRole.ASSISTANT,
            content=content,
            timestamp=datetime.now()
        )
        
        return ChatResponse(
            message=response_message,
            processing_time=0.2,
            model_info={
                "model_name": "Alice-Demo-v1.0",
                "type": "Mock Language Model"
            }
        )
    
    def _generate_smart_response(self, user_input: str, messages: List[Message]) -> str:
        """生成智能回應"""
        # 檢查關鍵詞匹配
        for keyword, response in self.responses.items():
            if keyword in user_input:
                return response
        
        # 記憶提取模式
        memory_patterns = [
            (r"(?:我的|我把)(.+?)(?:在|放在|是在)(.+)", "記住了！您的{item}在{location}。"),
            (r"(.+?)(?:是|在)(.+?)(?:上|裡|旁|附近)", "明白！{item}在{location}，我記下來了。"),
            (r"記住(.+)", "好的，我會記住：{info}"),
            (r"(?:什麼時候|何時)(.+)", "關於{topic}的時間，我需要更多信息才能幫您記住。"),
        ]
        
        for pattern, template in memory_patterns:
            match = re.search(pattern, user_input)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    return template.format(item=groups[0].strip(), location=groups[1].strip())
                elif len(groups) == 1:
                    return template.format(info=groups[0].strip(), topic=groups[0].strip())
        
        # 問題回應
        if "?" in user_input or "什麼" in user_input or "哪裡" in user_input or "where" in user_input.lower():
            return "這是個很好的問題！如果您之前告訴過我相關信息，我會努力回憶。如果沒有，請告訴我更多詳情，我會記住的。"
        
        # 默認智能回應
        default_responses = [
            "我理解您的意思。作為您的助手，我會盡力幫助您管理和記憶重要信息。",
            "謝謝您與我分享這個信息。我會記住這個內容，以便之後為您提供幫助。",
            "這很有趣！我正在學習如何更好地理解和幫助您。有什麼特別需要我記住的嗎？",
            "我會認真考慮您說的話。如果有什麼重要信息需要我記住，請明確告訴我。"
        ]
        
        # 根據輸入長度選擇回應
        import random
        return random.choice(default_responses)


class InMemoryRepository(ChatbotRepository):
    """內存數據庫，用於演示"""
    
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
    
    async def save_conversation(self, conversation: Conversation) -> None:
        """保存對話到內存"""
        self.conversations[conversation.id] = conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """從內存獲取對話"""
        return self.conversations.get(conversation_id)
    
    async def list_conversations(self, limit: int = 50) -> List[Conversation]:
        """列出對話"""
        conversations = list(self.conversations.values())
        conversations.sort(key=lambda x: x.updated_at, reverse=True)
        return conversations[:limit]


class AliceDemoBot:
    """Alice 演示聊天機器人"""
    
    def __init__(self):
        # 基礎設施層
        self.repository = InMemoryRepository()
        self.language_model = MockLanguageModel()
        
        # 用例層
        self.chatbot_use_case = ChatbotUseCase(
            self.language_model,
            self.repository,
            ModelConfig(model_name="Alice-Demo-v1.0")
        )
        self.memory_use_case = MemoryUseCase(self.repository)
        
        # 適配器層
        self.controller = ChatbotController(
            self.chatbot_use_case,
            self.memory_use_case,
            None  # 演示版不需要模型管理
        )
        self.presenter = ConsolePresenter()
    
    async def initialize(self) -> None:
        """初始化演示機器人"""
        self.presenter.show_welcome()
        
        # 載入模擬模型
        self.presenter.show_loading("正在載入 Alice 演示模型...")
        await self.language_model.load_model(ModelConfig("Alice-Demo-v1.0"))
        self.presenter.show_success("Alice 演示模型載入完成！")
        
        # 開始對話
        system_prompt = """您是 Alice，一個友善且具有記憶能力的 AI 助手。您的主要特色：
1. 能夠記住用戶告訴您的重要信息（如物品位置、重要日期等）
2. 在對話中主動使用記憶的信息來提供幫助
3. 保持友善和有幫助的語調
4. 當用戶詢問之前提到的信息時，能夠準確回憶

這是一個演示版本，展示了 Clean Architecture 的設計原則。"""
        
        conversation_id = await self.controller.start_new_conversation(system_prompt)
        self.presenter.show_info(f"新對話已開始 (ID: {conversation_id[:8]}...)")
        
        # 預先存儲一些演示記憶
        await self.controller.store_memory("錢包位置", "主桌", "演示數據")
        await self.controller.store_memory("車鑰匙位置", "門旁牆架", "演示數據") 
        await self.controller.store_memory("Mr.A生日", "2001/06/19", "演示數據")
        self.presenter.show_info("已載入一些演示記憶數據")
    
    async def run_demo(self) -> None:
        """運行演示"""
        self.presenter.show_info("\n🎯 演示模式說明:")
        self.presenter.show_info("• 這是使用模擬語言模型的演示版本")
        self.presenter.show_info("• 展示了 Clean Architecture 的分層結構")
        self.presenter.show_info("• 包含記憶管理、對話歷史等功能")
        self.presenter.show_info("• 輸入 '/quit' 退出演示\n")
        
        try:
            while True:
                try:
                    user_input = input("💬 您: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                
                if not user_input:
                    continue
                
                # 處理指令
                if user_input.startswith("/"):
                    await self._handle_command(user_input)
                    continue
                
                # 發送訊息
                self.presenter.show_loading("正在思考回應...")
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
            self.presenter.show_info("感謝使用 Alice 演示版！👋")
    
    async def _handle_command(self, command: str) -> None:
        """處理特殊指令"""
        parts = command[1:].split(maxsplit=2)
        cmd = parts[0].lower()
        
        if cmd in ["quit", "exit"]:
            raise KeyboardInterrupt
        
        elif cmd == "demo":
            await self._show_demo_info()
        
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
                self.presenter.show_error("用法: /memory <鍵> <值>")
        
        elif cmd == "history":
            result = await self.controller.get_conversation_history()
            if result["success"]:
                self.presenter.show_conversation_history(result)
            else:
                self.presenter.show_error(result["error"])
        
        elif cmd == "help":
            self._show_help()
        
        else:
            self.presenter.show_error(f"未知指令: /{cmd}")
    
    async def _show_demo_info(self) -> None:
        """顯示演示信息"""
        info = """
🏗️ **Alice Chatbot 架構演示**

**Clean Architecture 分層:**
1. **實體層** - 核心業務對象 (Message, Conversation)
2. **用例層** - 業務邏輯 (ChatbotUseCase, MemoryUseCase)  
3. **適配器層** - 接口適配 (Controller, Presenter)
4. **基礎設施層** - 外部服務 (MockLanguageModel, InMemoryRepository)

**演示功能:**
• 💬 智能對話 - 上下文感知的回應生成
• 🧠 記憶管理 - 自動提取和存儲重要信息  
• 📝 對話歷史 - 完整的對話記錄和檢索
• 🎯 指令系統 - 特殊功能的快速訪問

**架構優勢:**
• ✅ 可測試性 - 每層都可以獨立測試
• ✅ 可維護性 - 清晰的職責分離
• ✅ 可擴展性 - 容易添加新功能
• ✅ 可替換性 - 組件可以輕易替換
        """
        self.presenter.show_info(info)
    
    def _show_help(self) -> None:
        """顯示幫助信息"""
        help_text = """
**可用指令:**
• `/demo` - 顯示架構演示信息
• `/memory <鍵> <值>` - 存儲記憶項目
• `/history` - 查看對話歷史
• `/help` - 顯示此幫助信息
• `/quit` - 退出演示

**演示對話範例:**
• "我的錢包在書桌上"
• "車鑰匙掛在門旁"
• "錢包在哪裡？"
• "明天有重要會議"
        """
        self.presenter.show_info(help_text)


async def main():
    """主函數"""
    print("🚀 啟動 Alice Chatbot 演示版...")
    
    demo_bot = AliceDemoBot()
    
    try:
        await demo_bot.initialize()
        await demo_bot.run_demo()
    except Exception as e:
        print(f"❌ 演示過程中發生錯誤: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
