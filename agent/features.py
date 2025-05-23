"""
Advanced features and utilities for Alice Chatbot.
This module contains additional functionality that extends the core chatbot.
"""
import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from .entities import Message, Conversation, MessageRole


@dataclass
class MemoryItem:
    """Structured memory item."""
    key: str
    value: str
    category: str
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    confidence: float = 1.0
    context: Optional[str] = None


class MemoryExtractor:
    """Extract memory items from conversations."""
    
    # Patterns for extracting factual information
    MEMORY_PATTERNS = [
        # Location patterns
        (r"(?:my|the)\s+(.+?)\s+(?:is|are)\s+(?:at|in|on)\s+(.+)", "location"),
        (r"(.+?)\s+(?:is|are)\s+(?:located|placed|stored)\s+(?:at|in|on)\s+(.+)", "location"),
        
        # Personal info patterns  
        (r"(?:my|the)\s+(.+?)\s+(?:is|are)\s+(.+)", "personal"),
        (r"I\s+(?:am|have|work)\s+(.+)", "personal"),
        
        # Schedule/event patterns
        (r"(.+?)\s+(?:is|will be)\s+(?:on|at)\s+(.+)", "schedule"),
        (r"(?:remember|remind)\s+(?:me|that)\s+(.+)", "reminder"),
        
        # Preference patterns
        (r"I\s+(?:like|love|prefer|hate|dislike)\s+(.+)", "preference"),
    ]
    
    def extract_memories(self, conversation: Conversation) -> List[MemoryItem]:
        """Extract memory items from conversation."""
        memories = []
        
        for message in conversation.messages:
            if message.role == MessageRole.USER:
                extracted = self._extract_from_text(message.content)
                memories.extend(extracted)
        
        return memories
    
    def _extract_from_text(self, text: str) -> List[MemoryItem]:
        """Extract memories from a single text."""
        memories = []
        text_lower = text.lower()
        
        for pattern, category in self.MEMORY_PATTERNS:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                if len(match.groups()) >= 2:
                    key = match.group(1).strip()
                    value = match.group(2).strip()
                    
                    memory = MemoryItem(
                        key=key,
                        value=value,
                        category=category,
                        created_at=datetime.now(),
                        last_accessed=datetime.now(),
                        context=text
                    )
                    memories.append(memory)
        
        return memories


class ConversationAnalyzer:
    """Analyze conversations for insights and patterns."""
    
    def analyze_conversation(self, conversation: Conversation) -> Dict[str, Any]:
        """Analyze a conversation and return insights."""
        user_messages = [m for m in conversation.messages if m.role == MessageRole.USER]
        assistant_messages = [m for m in conversation.messages if m.role == MessageRole.ASSISTANT]
        
        analysis = {
            "message_count": len(conversation.messages),
            "user_message_count": len(user_messages),
            "assistant_message_count": len(assistant_messages),
            "conversation_length": len(' '.join([m.content for m in conversation.messages])),
            "topics": self._extract_topics(conversation.messages),
            "sentiment": self._analyze_sentiment(user_messages),
            "questions_asked": self._count_questions(user_messages),
            "duration": (conversation.updated_at - conversation.created_at).total_seconds() / 60,  # minutes
        }
        
        return analysis
    
    def _extract_topics(self, messages: List[Message]) -> List[str]:
        """Extract main topics from messages."""
        # Simple keyword extraction (could be enhanced with NLP)
        text = ' '.join([m.content for m in messages]).lower()
        
        # Common topic keywords
        topic_keywords = {
            'work': ['work', 'job', 'office', 'meeting', 'project', 'deadline'],
            'personal': ['family', 'home', 'personal', 'life', 'health'],
            'technology': ['computer', 'software', 'app', 'tech', 'digital'],
            'schedule': ['time', 'date', 'schedule', 'appointment', 'calendar'],
            'location': ['place', 'location', 'address', 'where', 'room'],
            'memory': ['remember', 'recall', 'memory', 'forget', 'stored']
        }
        
        found_topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                found_topics.append(topic)
        
        return found_topics
    
    def _analyze_sentiment(self, messages: List[Message]) -> str:
        """Simple sentiment analysis."""
        if not messages:
            return "neutral"
        
        text = ' '.join([m.content for m in messages]).lower()
        
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'happy', 'pleased']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'angry', 'frustrated', 'disappointed', 'sad']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _count_questions(self, messages: List[Message]) -> int:
        """Count questions in messages."""
        question_count = 0
        for message in messages:
            question_count += message.content.count('?')
        return question_count


class ContextManager:
    """Manage conversation context and relevance."""
    
    def __init__(self, max_context_length: int = 10):
        self.max_context_length = max_context_length
    
    def get_relevant_context(
        self, 
        conversation: Conversation, 
        current_message: str,
        memories: Optional[List[MemoryItem]] = None
    ) -> List[Message]:
        """Get relevant context for the current message."""
        # Start with recent messages
        context_messages = conversation.get_context_messages(self.max_context_length)
        
        # Add relevant memories as system messages
        if memories:
            relevant_memories = self._find_relevant_memories(current_message, memories)
            for memory in relevant_memories[:3]:  # Limit to 3 most relevant
                memory_message = Message(
                    id="",
                    role=MessageRole.SYSTEM,
                    content=f"Memory: {memory.key} is {memory.value}",
                    timestamp=datetime.now(),
                    metadata={"type": "memory", "confidence": memory.confidence}
                )
                context_messages.insert(-1, memory_message)  # Insert before last message
        
        return context_messages
    
    def _find_relevant_memories(self, query: str, memories: List[MemoryItem]) -> List[MemoryItem]:
        """Find memories relevant to the query."""
        query_lower = query.lower()
        relevant = []
        
        for memory in memories:
            # Simple relevance scoring
            score = 0
            if memory.key.lower() in query_lower:
                score += 2
            if any(word in query_lower for word in memory.value.lower().split()):
                score += 1
            if memory.category in query_lower:
                score += 1
            
            if score > 0:
                memory.confidence = min(1.0, score / 3.0)
                relevant.append(memory)
        
        # Sort by relevance
        relevant.sort(key=lambda x: x.confidence, reverse=True)
        return relevant


class ResponseEnhancer:
    """Enhance chatbot responses with additional features."""
    
    def enhance_response(
        self, 
        response_content: str, 
        context: Dict[str, Any]
    ) -> str:
        """Enhance response with context-aware improvements."""
        enhanced = response_content
        
        # Add memory references if relevant
        if context.get("memories_used"):
            enhanced += self._add_memory_references(context["memories_used"])
        
        # Add helpful suggestions
        if context.get("user_question_count", 0) > 0:
            enhanced += self._add_helpful_suggestions(context)
        
        # Format for better readability
        enhanced = self._format_response(enhanced)
        
        return enhanced
    
    def _add_memory_references(self, memories: List[MemoryItem]) -> str:
        """Add memory references to response."""
        if not memories:
            return ""
        
        references = "\n\n📝 Based on what I remember:\n"
        for memory in memories:
            references += f"- {memory.key}: {memory.value}\n"
        
        return references
    
    def _add_helpful_suggestions(self, context: Dict[str, Any]) -> str:
        """Add helpful suggestions based on context."""
        suggestions = []
        
        if "location" in context.get("topics", []):
            suggestions.append("💡 Tip: I can help you remember where you put things!")
        
        if "schedule" in context.get("topics", []):
            suggestions.append("💡 Tip: I can remember important dates and deadlines for you!")
        
        if suggestions:
            return "\n\n" + "\n".join(suggestions)
        
        return ""
    
    def _format_response(self, response: str) -> str:
        """Format response for better readability."""
        # Add emoji for common expressions
        response = re.sub(r'\b(remember|recall)\b', '🧠 \\1', response, flags=re.IGNORECASE)
        response = re.sub(r'\b(location|place)\b', '📍 \\1', response, flags=re.IGNORECASE)
        response = re.sub(r'\b(time|date|schedule)\b', '📅 \\1', response, flags=re.IGNORECASE)
        
        return response
