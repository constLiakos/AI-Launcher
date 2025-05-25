from typing import List, Dict, Any
from datetime import datetime

class ConversationManager:
    """Manages conversation history for context in API requests."""
    
    def __init__(self, logger, max_conversations: int = 5):
        self.logger = logger
        self.max_conversations = max_conversations
        self.conversations: List[Dict[str, Any]] = []
    
    def add_conversation(self, user_prompt: str, assistant_response: str):
        """Add a new conversation to history."""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user": user_prompt.strip(),
            "assistant": assistant_response.strip()
        }
        
        self.conversations.append(conversation)
        
        # Keep only the last N conversations
        if len(self.conversations) > self.max_conversations:
            removed = self.conversations.pop(0)
            self.logger.debug(f"Removed oldest conversation from history")
        
        self.logger.debug(f"Added conversation to history. Total: {len(self.conversations)}")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history formatted for API requests."""
        history = []
        
        for conv in self.conversations:
            # Add user message
            history.append({
                "role": "user",
                "content": conv["user"]
            })
            # Add assistant response
            history.append({
                "role": "assistant", 
                "content": conv["assistant"]
            })
        
        self.logger.debug(f"Retrieved conversation history with {len(history)} messages")
        return history
    
    def clear_history(self):
        """Clear all conversation history."""
        self.conversations.clear()
        self.logger.debug("Conversation history cleared")
    
    def get_conversation_count(self) -> int:
        """Get the number of conversations in history."""
        return len(self.conversations)
    
    def get_last_conversation(self) -> Dict[str, Any]:
        """Get the most recent conversation."""
        return self.conversations[-1] if self.conversations else None