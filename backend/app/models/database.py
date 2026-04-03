"""
Luigi Chat - Database Models
"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models import Base
from datetime import datetime
import uuid


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # 'admin' | 'user'
    
    # UI Preferences
    theme = Column(String(50), default="dark")
    primary_color = Column(String(20), default="#7000FF")
    font_size = Column(String(20), default="medium")
    compact_mode = Column(Boolean, default=False)
    
    # Model Preferences
    default_model = Column(String(50), default="luigi-thinking")
    voice_enabled = Column(Boolean, default=False)
    voice_id = Column(String(100), default="male-qn-qingse")
    speech_speed = Column(String(10), default="1.0")
    speech_emotion = Column(String(20), default="neutral")
    
    # LiteLLM
    litellm_key = Column(String(255))
    litellm_user_id = Column(String(255))
    
    # Status
    status = Column(String(20), default="active")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_at = Column(DateTime)
    
    # Relationships
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    files = relationship("File", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "email": self.email,
            "role": self.role,
            "theme": self.theme,
            "primary_color": self.primary_color,
            "default_model": self.default_model,
            "voice_enabled": self.voice_enabled,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Chat(Base):
    """Chat model"""
    __tablename__ = "chats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), default="New Chat")
    model = Column(String(50), default="luigi-thinking")
    
    # Metadata
    tags = Column(ARRAY(Text), default=[])
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folders.id", ondelete="SET NULL"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan", order_by="Message.created_at")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "model": self.model,
            "tags": self.tags or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Message(Base):
    """Message model"""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' | 'assistant' | 'system'
    content = Column(Text, nullable=False)
    
    # For messages with images
    image_urls = Column(ARRAY(Text), default=[])
    
    # Model info
    model = Column(String(50))
    tokens_used = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "chat_id": str(self.chat_id),
            "role": self.role,
            "content": self.content,
            "image_urls": self.image_urls or [],
            "model": self.model,
            "tokens_used": self.tokens_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class File(Base):
    """File metadata model"""
    __tablename__ = "files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # MiniMax file info
    minimax_file_id = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # 'document' | 'audio' | 'image'
    size_bytes = Column(Integer, nullable=False)
    
    # Status
    status = Column(String(20), default="active")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="files")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "minimax_file_id": self.minimax_file_id,
            "filename": self.filename,
            "file_type": self.file_type,
            "size_bytes": self.size_bytes,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Folder(Base):
    """Folder model for organizing chats"""
    __tablename__ = "folders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("folders.id", ondelete="CASCADE"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
