import logging
import os
from pathlib import Path
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, Text, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import uuid
from utils.constants import Database

# SQLAlchemy Models
Base = declarative_base()

class ConversationModel(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    conversation_metadata = Column(Text)  # JSON string - renamed from 'metadata'
    message_count = Column(Integer, default=0)
    is_archived = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    tags = Column(Text)  # JSON array as string
    
    # Relationship
    messages = relationship("MessageModel", back_populates="conversation", cascade="all, delete-orphan")

class MessageModel(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    content = Column(Text, nullable=False)
    sender = Column(String, nullable=False)  # user, assistant, system, tool
    timestamp = Column(DateTime, default=datetime.utcnow)
    tool_calls = Column(Text)  # JSON string
    message_metadata = Column(Text)  # JSON string - renamed from 'metadata'
    parent_message_id = Column(String, ForeignKey("messages.id"))
    is_deleted = Column(Boolean, default=False)
    edit_count = Column(Integer, default=0)
    
    # Relationships
    conversation = relationship("ConversationModel", back_populates="messages")
    parent = relationship("MessageModel", remote_side="MessageModel.id")


# Pydantic Schemas
class MessageCreate(BaseModel):
    content: str
    sender: str = Field(..., pattern="^(user|assistant|system|tool)$")
    tool_calls: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    parent_message_id: Optional[str] = None

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    tool_calls: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    content: str
    sender: str
    timestamp: datetime
    tool_calls: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    parent_message_id: Optional[str] = None
    edit_count: int = 0
    
    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_archived: Optional[bool] = None
    is_favorite: Optional[bool] = None

class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    message_count: int
    is_archived: bool = False
    is_favorite: bool = False
    tags: Optional[List[str]] = None
    
    class Config:
        from_attributes = True

# Main Manager Class
class AIConversationManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_connection_string = Database.CONVERSATIONS_DATABASE_CONNECTION_STRING
        self.logger.info(f"Initializing AIConversationManager with database: {self.db_connection_string}")
        
        try:
            # Create database directory if it doesn't exist (for SQLite)
            if self.db_connection_string.startswith('sqlite:///'):
                # Extract the database path from connection string
                db_path = Path(self.db_connection_string.replace('sqlite:///', ''))
                db_dir = db_path.parent
                
                self.logger.info(f"Database path: {db_path}")
                self.logger.info(f"Database directory: {db_dir}")
                
                # More detailed logging
                self.logger.info(f"Directory exists before creation: {db_dir.exists()}")
                self.logger.info(f"Directory is absolute: {db_dir.is_absolute()}")
                self.logger.info(f"Current working directory: {os.getcwd()}")
                
                # Cross-platform user info
                try:
                    if hasattr(os, 'getuid'):
                        self.logger.info(f"Current user ID: {os.getuid()}")
                    else:
                        self.logger.info(f"Current user: {os.getenv('USERNAME', 'unknown')}")
                except Exception as e:
                    self.logger.info(f"Could not get user info: {e}")
                
                # Create directory if it doesn't exist with proper error handling
                try:
                    if not db_dir.exists():
                        self.logger.info(f"Attempting to create directory: {db_dir}")
                        db_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
                        self.logger.info(f"mkdir() completed")
                    
                    # Check if directory was actually created
                    self.logger.info(f"Directory exists after creation: {db_dir.exists()}")
                    
                    if db_dir.exists():
                        # Check directory permissions
                        self.logger.info(f"Directory is readable: {os.access(db_dir, os.R_OK)}")
                        self.logger.info(f"Directory is writable: {os.access(db_dir, os.W_OK)}")
                        self.logger.info(f"Directory is executable: {os.access(db_dir, os.X_OK)}")
                        
                        # List directory contents
                        try:
                            contents = list(db_dir.iterdir())
                            self.logger.info(f"Directory contents: {contents}")
                        except Exception as e:
                            self.logger.error(f"Cannot list directory contents: {e}")
                    else:
                        self.logger.error("Directory was not created successfully")
                        
                    # Check if database file exists and is writable
                    if db_path.exists():
                        self.logger.info(f"Database file exists: {db_path}")
                        self.logger.info(f"Database file is writable: {os.access(db_path, os.W_OK)}")
                    else:
                        self.logger.info(f"Database file does not exist (will be created): {db_path}")
                        
                except (OSError, PermissionError) as e:
                    self.logger.error(f"Failed to create/access database directory: {e}")
                    raise
            
            # Create engine with proper settings for SQLite
            if self.db_connection_string.startswith('sqlite:///'):
                self.logger.info("Creating SQLAlchemy engine...")
                self.engine = create_engine(
                    self.db_connection_string,
                    connect_args={
                        "check_same_thread": False,
                        "timeout": 20
                    },
                    echo=False,
                    pool_pre_ping=True
                )
            else:
                self.engine = create_engine(self.db_connection_string)
            
            self.logger.info("Creating SessionLocal...")
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create all tables
            self.logger.info("Creating database tables...")
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("Database engine created and tables initialized successfully")
            
            # Test the connection
            self._test_connection()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    def _test_connection(self):
        """Test database connection"""
        try:
            with self.get_db() as db:
                # Simple query to test connection - using text() for raw SQL
                result = db.execute(text("SELECT 1")).fetchone()
                self.logger.info("Database connection test successful")
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            raise
        
    def get_db(self) -> Session:
        """Get database session with context manager support"""
        return self.SessionLocal()
    
    # Conversation Operations
    def create_conversation(self, conversation_data: ConversationCreate) -> ConversationResponse:
        self.logger.info(f"Creating new conversation with title: {conversation_data.title}")
        
        try:
            with self.get_db() as db:
                if not conversation_data.title:
                    conversation_data.title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    self.logger.debug(f"Generated title: {conversation_data.title}")
                
                db_conversation = ConversationModel(
                    title=conversation_data.title,
                    conversation_metadata=json.dumps(conversation_data.metadata) if conversation_data.metadata else None,
                    tags=json.dumps(conversation_data.tags) if conversation_data.tags else None
                )
                
                db.add(db_conversation)
                db.commit()
                db.refresh(db_conversation)
                
                self.logger.info(f"Conversation created successfully with ID: {db_conversation.id}")
                return self._conversation_to_response(db_conversation)
                
        except Exception as e:
            self.logger.error(f"Failed to create conversation: {e}")
            raise

    def get_conversation(self, conversation_id: str) -> Optional[ConversationResponse]:
        self.logger.debug(f"Retrieving conversation with ID: {conversation_id}")
        
        try:
            with self.get_db() as db:
                conversation = db.query(ConversationModel).filter(ConversationModel.id == conversation_id).first()
                
                if conversation:
                    self.logger.debug(f"Conversation found: {conversation.title}")
                    return self._conversation_to_response(conversation)
                else:
                    self.logger.warning(f"Conversation not found with ID: {conversation_id}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Failed to retrieve conversation {conversation_id}: {e}")
            raise
    
    
    def get_conversations(self, include_archived: bool = False, limit: int = 100) -> List[ConversationResponse]:
        self.logger.debug(f"Retrieving conversations (include_archived: {include_archived}, limit: {limit})")
        
        try:
            with self.get_db() as db:
                query = db.query(ConversationModel)
                
                if not include_archived:
                    query = query.filter(ConversationModel.is_archived == False)
                
                conversations = query.order_by(ConversationModel.updated_at.desc()).limit(limit).all()
                
                self.logger.info(f"Retrieved {len(conversations)} conversations")
                return [self._conversation_to_response(conv) for conv in conversations]
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve conversations: {e}")
            raise
    
    def update_conversation(self, conversation_id: str, update_data: ConversationUpdate) -> Optional[ConversationResponse]:
        self.logger.info(f"Updating conversation {conversation_id}")
        
        try:
            with self.get_db() as db:
                conversation = db.query(ConversationModel).filter(ConversationModel.id == conversation_id).first()
                
                if not conversation:
                    self.logger.warning(f"Cannot update - conversation not found: {conversation_id}")
                    return None
                
                update_dict = update_data.dict(exclude_unset=True)
                self.logger.debug(f"Updating fields: {list(update_dict.keys())}")
                
                for field, value in update_dict.items():
                    if field == "metadata" and value is not None:
                        setattr(conversation, "conversation_metadata", json.dumps(value))
                    elif field == "tags" and value is not None:
                        setattr(conversation, field, json.dumps(value))
                    else:
                        setattr(conversation, field, value)
                
                conversation.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(conversation)
                
                self.logger.info(f"Conversation {conversation_id} updated successfully")
                return self._conversation_to_response(conversation)
                
        except Exception as e:
            self.logger.error(f"Failed to update conversation {conversation_id}: {e}")
            raise
    
    def delete_conversation(self, conversation_id: str) -> bool:
        self.logger.info(f"Deleting conversation {conversation_id}")
        
        try:
            with self.get_db() as db:
                conversation = db.query(ConversationModel).filter(ConversationModel.id == conversation_id).first()
                
                if conversation:
                    message_count = len(conversation.messages)
                    db.delete(conversation)
                    db.commit()
                    
                    self.logger.info(f"Conversation {conversation_id} deleted successfully (including {message_count} messages)")
                    return True
                else:
                    self.logger.warning(f"Cannot delete - conversation not found: {conversation_id}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            raise
    
    # Message Operations
    def add_message(self, conversation_id: str, message_data: MessageCreate) -> MessageResponse:
        self.logger.debug(f"Adding message to conversation {conversation_id} from {message_data.sender}")
        
        try:
            with self.get_db() as db:
                db_message = MessageModel(
                    conversation_id=conversation_id,
                    content=message_data.content,
                    sender=message_data.sender,
                    tool_calls=json.dumps(message_data.tool_calls) if message_data.tool_calls else None,
                    message_metadata=json.dumps(message_data.metadata) if message_data.metadata else None,
                    parent_message_id=message_data.parent_message_id
                )
                db.add(db_message)
                
                # Update conversation message count
                conversation = db.query(ConversationModel).filter(ConversationModel.id == conversation_id).first()
                if conversation:
                    conversation.message_count += 1
                    conversation.updated_at = datetime.utcnow()
                    self.logger.debug(f"Updated conversation message count to {conversation.message_count}")
                else:
                    self.logger.warning(f"Conversation {conversation_id} not found when adding message")
                
                db.commit()
                db.refresh(db_message)
                
                self.logger.info(f"Message added successfully with ID: {db_message.id}")
                return self._message_to_response(db_message)
                
        except Exception as e:
            self.logger.error(f"Failed to add message to conversation {conversation_id}: {e}")
            raise

    
    def get_messages(self, conversation_id: str, limit: int = None, include_deleted: bool = False) -> List[MessageResponse]:
        self.logger.debug(f"Retrieving messages for conversation {conversation_id} (limit: {limit}, include_deleted: {include_deleted})")
        
        try:
            with self.get_db() as db:
                query = db.query(MessageModel).filter(MessageModel.conversation_id == conversation_id)
                
                if not include_deleted:
                    query = query.filter(MessageModel.is_deleted == False)
                
                query = query.order_by(MessageModel.timestamp.asc())
                
                if limit:
                    query = query.limit(limit)
                
                messages = query.all()
                
                self.logger.debug(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
                return [self._message_to_response(msg) for msg in messages]
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve messages for conversation {conversation_id}: {e}")
            raise
        
    # Helper methods
    def _conversation_to_response(self, conversation: ConversationModel) -> ConversationResponse:
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            metadata=json.loads(conversation.conversation_metadata) if conversation.conversation_metadata else None,
            message_count=conversation.message_count,
            is_archived=conversation.is_archived,
            is_favorite=conversation.is_favorite,
            tags=json.loads(conversation.tags) if conversation.tags else None
        )
    
    def _message_to_response(self, message: MessageModel) -> MessageResponse:
        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            content=message.content,
            sender=message.sender,
            timestamp=message.timestamp,
            tool_calls=json.loads(message.tool_calls) if message.tool_calls else None,
            metadata=json.loads(message.message_metadata) if message.message_metadata else None,
            parent_message_id=message.parent_message_id,
            edit_count=message.edit_count
        )

# # Usage Example
# if __name__ == "__main__":
#     manager = AIConversationManager()
    
#     # Create conversation
#     conv_data = ConversationCreate(title="Test Conversation", tags=["ai", "test"])
#     conversation = manager.create_conversation(conv_data)
    
#     # Add message
#     msg_data = MessageCreate(
#         content="Hello, how are you?",
#         sender="user"
#     )
#     message = manager.add_message(conversation.id, msg_data)
    
#     # Get messages
#     messages = manager.get_messages(conversation.id)
#     print(f"Messages: {len(messages)}")