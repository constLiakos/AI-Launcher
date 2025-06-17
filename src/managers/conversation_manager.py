import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.constants import Conversation
from utils.database import AIConversationManager, ConversationCreate, MessageCreate, ConversationResponse, MessageResponse, ConversationUpdate

class ConversationManager:
    """Manages conversation history for context in API requests using database storage."""
    
    def __init__(self, max_conversations: int = Conversation.DEFAULT_CONVERSATION_HISTORY_LIMIT, db_manager: Optional[AIConversationManager] = None):
        self.logger = logging.getLogger(__name__)
        self.max_conversations = max_conversations
        self.current_conversation_id: Optional[str] = None
        
        # Initialize or use provided database manager
        if db_manager:
            self.db_manager = db_manager
        else:
            self.db_manager = AIConversationManager()
        
        self.logger.info(f"ConversationManager initialized with max_conversations: {max_conversations}")
    
    def start_new_conversation(self, title: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start a new conversation and return its ID."""
        try:
            conv_data = ConversationCreate(
                title=title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                metadata=metadata,
                tags=["api_conversation"]
            )
            
            conversation = self.db_manager.create_conversation(conv_data)
            self.current_conversation_id = conversation.id
            
            self.logger.info(f"Started new conversation: {conversation.id} - {conversation.title}")
            return conversation.id
            
        except Exception as e:
            self.logger.error(f"Failed to start new conversation: {e}")
            raise
    
    def add_conversation(self, user_prompt: str, assistant_response: str, 
                        conversation_id: Optional[str] = None,
                        user_metadata: Optional[Dict[str, Any]] = None,
                        assistant_metadata: Optional[Dict[str, Any]] = None):
        """Add a new conversation exchange to the database."""
        try:
            # Use current conversation or create new one
            if conversation_id:
                target_conversation_id = conversation_id
            elif self.current_conversation_id:
                target_conversation_id = self.current_conversation_id
            else:
                # Create new conversation if none exists
                target_conversation_id = self.start_new_conversation()
            
            # Add user message
            user_msg_data = MessageCreate(
                content=user_prompt.strip(),
                sender="user",
                metadata=user_metadata
            )
            user_message = self.db_manager.add_message(target_conversation_id, user_msg_data)
            
            # Add assistant message
            assistant_msg_data = MessageCreate(
                content=assistant_response.strip(),
                sender="assistant",
                metadata=assistant_metadata,
                parent_message_id=user_message.id  # Link assistant response to user message
            )
            assistant_message = self.db_manager.add_message(target_conversation_id, assistant_msg_data)
            
            self.logger.debug(f"Added conversation exchange to {target_conversation_id}")
            
            # Clean up old conversations if we exceed the limit
            self._cleanup_old_conversations()
            
            return {
                "conversation_id": target_conversation_id,
                "user_message_id": user_message.id,
                "assistant_message_id": assistant_message.id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to add conversation: {e}")
            raise
    
    def get_conversation_history(self, conversation_id: Optional[str] = None, 
                               limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Get conversation history formatted for API requests."""
        try:
            # Use current conversation if none specified
            target_conversation_id = conversation_id or self.current_conversation_id
            
            if not target_conversation_id:
                self.logger.debug("No conversation ID available for history retrieval")
                return []
            
            # Get messages from database
            messages = self.db_manager.get_messages(
                target_conversation_id, 
                limit=limit or (self.max_conversations * 2)  # 2 messages per conversation (user + assistant)
            )
            
            # Format for API
            history = []
            for msg in messages:
                history.append({
                    "role": msg.sender,
                    "content": msg.content
                })
            
            self.logger.debug(f"Retrieved conversation history with {len(history)} messages from {target_conversation_id}")
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get conversation history: {e}")
            return []
    
    def get_recent_conversations_history(self, max_messages: Optional[int] = None) -> List[Dict[str, str]]:
        """Get history from recent conversations for context."""
        try:
            # Get recent conversations
            conversations = self.db_manager.get_conversations(
                include_archived=False, 
                limit=self.max_conversations
            )
            
            if not conversations:
                return []
            
            all_messages = []
            total_messages = 0
            max_msgs = max_messages or (self.max_conversations * 2)
            
            # Collect messages from recent conversations
            for conv in conversations:
                if total_messages >= max_msgs:
                    break
                    
                messages = self.db_manager.get_messages(
                    conv.id, 
                    limit=max_msgs - total_messages
                )
                
                for msg in messages:
                    if total_messages >= max_msgs:
                        break
                    all_messages.append({
                        "role": msg.sender,
                        "content": msg.content,
                        "timestamp": msg.timestamp
                    })
                    total_messages += 1
            
            # Sort by timestamp and format for API
            all_messages.sort(key=lambda x: x["timestamp"])
            history = [{"role": msg["role"], "content": msg["content"]} for msg in all_messages]
            
            self.logger.debug(f"Retrieved recent conversations history with {len(history)} messages")
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get recent conversations history: {e}")
            return []
    
    def clear_current_conversation(self):
        """Clear the current conversation reference."""
        if self.current_conversation_id:
            self.logger.debug(f"Cleared current conversation reference: {self.current_conversation_id}")
            self.current_conversation_id = None
    
    def archive_conversation(self, conversation_id: Optional[str] = None) -> bool:
        """Archive a conversation."""
        try:
            target_id = conversation_id or self.current_conversation_id
            if not target_id:
                self.logger.warning("No conversation ID to archive")
                return False
            
            update_data = ConversationUpdate(is_archived=True)
            result = self.db_manager.update_conversation(target_id, update_data)
            
            if result:
                self.logger.info(f"Archived conversation: {target_id}")
                if target_id == self.current_conversation_id:
                    self.current_conversation_id = None
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to archive conversation: {e}")
            return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation permanently."""
        try:
            result = self.db_manager.delete_conversation(conversation_id)
            if result:
                self.logger.info(f"Deleted conversation: {conversation_id}")
                if conversation_id == self.current_conversation_id:
                    self.current_conversation_id = None
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to delete conversation: {e}")
            return False
    
    def get_conversation_count(self) -> int:
        """Get the total number of active conversations."""
        try:
            conversations = self.db_manager.get_conversations(include_archived=False)
            return len(conversations)
        except Exception as e:
            self.logger.error(f"Failed to get conversation count: {e}")
            return 0
    
    def get_current_conversation_info(self) -> Optional[ConversationResponse]:
        """Get information about the current conversation."""
        if not self.current_conversation_id:
            return None
        
        try:
            return self.db_manager.get_conversation(self.current_conversation_id)
        except Exception as e:
            self.logger.error(f"Failed to get current conversation info: {e}")
            return None
    
    def get_last_conversation(self) -> Optional[Dict[str, Any]]:
        """Get the most recent conversation exchange."""
        try:
            if not self.current_conversation_id:
                return None
            
            messages = self.db_manager.get_messages(self.current_conversation_id, limit=2)
            if len(messages) >= 2:
                # Assuming the last two messages are user and assistant
                return {
                    "user": messages[-2].content if messages[-2].sender == "user" else messages[-1].content,
                    "assistant": messages[-1].content if messages[-1].sender == "assistant" else messages[-2].content,
                    "timestamp": messages[-1].timestamp.isoformat()
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get last conversation: {e}")
            return None
    
    def add_system_message(self, content: str, conversation_id: Optional[str] = None, 
                          metadata: Optional[Dict[str, Any]] = None):
        """Add a system message to the conversation."""
        try:
            target_conversation_id = conversation_id or self.current_conversation_id
            if not target_conversation_id:
                target_conversation_id = self.start_new_conversation()
            
            msg_data = MessageCreate(
                content=content,
                sender="system",
                metadata=metadata
            )
            
            message = self.db_manager.add_message(target_conversation_id, msg_data)
            self.logger.debug(f"Added system message to conversation {target_conversation_id}")
            return message
            
        except Exception as e:
            self.logger.error(f"Failed to add system message: {e}")
            raise
    
    def add_tool_message(self, content: str, tool_calls: Dict[str, Any], 
                        conversation_id: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None):
        """Add a tool message to the conversation."""
        try:
            target_conversation_id = conversation_id or self.current_conversation_id
            if not target_conversation_id:
                target_conversation_id = self.start_new_conversation()
            
            msg_data = MessageCreate(
                content=content,
                sender="tool",
                tool_calls=tool_calls,
                metadata=metadata
            )
            
            message = self.db_manager.add_message(target_conversation_id, msg_data)
            self.logger.debug(f"Added tool message to conversation {target_conversation_id}")
            return message
            
        except Exception as e:
            self.logger.error(f"Failed to add tool message: {e}")
            raise
    
    def _cleanup_old_conversations(self):
        """Archive old conversations if we exceed the maximum limit."""
        try:
            conversations = self.db_manager.get_conversations(include_archived=False)
            
            if len(conversations) > self.max_conversations:
                # Sort by last updated and archive the oldest ones
                conversations.sort(key=lambda x: x.updated_at)
                excess_count = len(conversations) - self.max_conversations
                
                update_data = ConversationUpdate(is_archived=True)
                
                for i in range(excess_count):
                    self.db_manager.update_conversation(conversations[i].id, update_data)
                    self.logger.debug(f"Auto-archived old conversation: {conversations[i].id}")
                    
        except Exception as e:
            self.logger.error(f"Failed to cleanup old conversations: {e}")

    def set_current_conversation(self, conversation_id: str):
        """Set the current active conversation."""
        # Verify the conversation exists
        conversation = self.db_manager.get_conversation(conversation_id)
        if conversation:
            self.current_conversation_id = conversation_id
            self.logger.debug(f"Set current conversation to: {conversation_id}")
        else:
            raise ValueError(f"Conversation {conversation_id} not found")
    
    def search_conversations(self, query: str, limit: int = 10) -> List[ConversationResponse]:
        """Search conversations by title or content (basic implementation)."""
        try:
            # This is a basic implementation - you might want to add full-text search
            conversations = self.db_manager.get_conversations(include_archived=True, limit=100)
            
            matching_conversations = []
            for conv in conversations:
                if query.lower() in conv.title.lower():
                    matching_conversations.append(conv)
                    if len(matching_conversations) >= limit:
                        break
            
            self.logger.debug(f"Found {len(matching_conversations)} conversations matching '{query}'")
            return matching_conversations
            
        except Exception as e:
            self.logger.error(f"Failed to search conversations: {e}")
            return []
        
    def clear_all_conversations(self) -> bool:
        """Clear all conversations by archiving them."""
        try:
            conversations = self.db_manager.get_conversations(include_archived=False)
            update_data = ConversationUpdate(is_archived=True)
            
            success_count = 0
            for conv in conversations:
                if self.db_manager.update_conversation(conv.id, update_data):
                    success_count += 1
            
            if conversations and success_count == len(conversations):
                self.current_conversation_id = None
                self.logger.info(f"Cleared {success_count} conversations")
                return True
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Failed to clear all conversations: {e}")
            return False
        

    def get_conversation_history_for_widget(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history formatted for the history widget."""
        try:
            conversations = self.db_manager.get_conversations(
                include_archived=False, 
                limit=limit
            )
            
            widget_data = []
            for conv in conversations:
                messages = self.db_manager.get_messages(conv.id, limit=2)
                if messages:
                    # Find user and assistant messages
                    user_msg = next((m for m in messages if m.sender == "user"), None)
                    assistant_msg = next((m for m in messages if m.sender == "assistant"), None)
                    
                    widget_data.append({
                        "conversation_id": conv.id,
                        "user_message": user_msg.content if user_msg else "No user message",
                        "assistant_response": assistant_msg.content if assistant_msg else "No response",
                        "timestamp": conv.updated_at.isoformat()
                    })
            
            return widget_data
            
        except Exception as e:
            self.logger.error(f"Failed to get conversation history for widget: {e}")
            return []