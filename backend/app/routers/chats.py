"""
Luigi Chat - Chats Router
Chat history and messaging
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
import json

from app.models import get_db
from app.models.database import Chat, Message, User
from app.routers.auth import get_current_user
from app.services.litellm import litellm_service

router = APIRouter()


class CreateChatRequest(BaseModel):
    title: Optional[str] = "New Chat"
    model: Optional[str] = "luigi-thinking"


class UpdateChatRequest(BaseModel):
    title: Optional[str] = None
    model: Optional[str] = None
    tags: Optional[List[str]] = None


class SendMessageRequest(BaseModel):
    content: str
    image_urls: Optional[List[str]] = []
    model: Optional[str] = None
    stream: Optional[bool] = True


class ChatResponse(BaseModel):
    id: str
    user_id: str
    title: str
    model: str
    tags: List[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class MessageResponse(BaseModel):
    id: str
    chat_id: str
    role: str
    content: str
    image_urls: List[str]
    model: Optional[str]
    tokens_used: Optional[int]
    created_at: Optional[str]


@router.get("/", response_model=List[ChatResponse])
async def list_chats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all chats for current user"""
    result = await db.execute(
        select(Chat)
        .where(Chat.user_id == current_user.id)
        .order_by(Chat.updated_at.desc())
    )
    chats = result.scalars().all()
    
    return [
        ChatResponse(
            id=str(c.id),
            user_id=str(c.user_id),
            title=c.title,
            model=c.model,
            tags=c.tags or [],
            created_at=c.created_at.isoformat() if c.created_at else None,
            updated_at=c.updated_at.isoformat() if c.updated_at else None,
        )
        for c in chats
    ]


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    request: CreateChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chat"""
    chat = Chat(
        user_id=current_user.id,
        title=request.title,
        model=request.model or current_user.default_model
    )
    
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    
    return ChatResponse(
        id=str(chat.id),
        user_id=str(chat.user_id),
        title=chat.title,
        model=chat.model,
        tags=chat.tags or [],
        created_at=chat.created_at.isoformat() if chat.created_at else None,
        updated_at=chat.updated_at.isoformat() if chat.updated_at else None,
    )


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific chat"""
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    return ChatResponse(
        id=str(chat.id),
        user_id=str(chat.user_id),
        title=chat.title,
        model=chat.model,
        tags=chat.tags or [],
        created_at=chat.created_at.isoformat() if chat.created_at else None,
        updated_at=chat.updated_at.isoformat() if chat.updated_at else None,
    )


@router.patch("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: UUID,
    request: UpdateChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a chat"""
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chat, field, value)
    
    await db.commit()
    await db.refresh(chat)
    
    return ChatResponse(
        id=str(chat.id),
        user_id=str(chat.user_id),
        title=chat.title,
        model=chat.model,
        tags=chat.tags or [],
        created_at=chat.created_at.isoformat() if chat.created_at else None,
        updated_at=chat.updated_at.isoformat() if chat.updated_at else None,
    )


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a chat"""
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    await db.delete(chat)
    await db.commit()


@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    chat_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all messages in a chat"""
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    
    return [
        MessageResponse(
            id=str(m.id),
            chat_id=str(m.chat_id),
            role=m.role,
            content=m.content,
            image_urls=m.image_urls or [],
            model=m.model,
            tokens_used=m.tokens_used,
            created_at=m.created_at.isoformat() if m.created_at else None,
        )
        for m in messages
    ]


@router.post("/{chat_id}/messages")
async def send_message(
    chat_id: UUID,
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message and get AI response"""
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    if not current_user.litellm_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No API key found. Please contact admin."
        )
    
    user_message = Message(
        chat_id=chat_id,
        role="user",
        content=request.content,
        image_urls=request.image_urls,
        model=request.model or chat.model
    )
    db.add(user_message)
    await db.commit()
    
    messages_for_llm = []
    
    result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
    )
    history = result.scalars().all()
    
    for msg in history:
        msg_content = [{"type": "text", "text": msg.content}]
        
        if msg.image_urls:
            for img_url in msg.image_urls:
                msg_content.append({"type": "image_url", "image_url": {"url": img_url}})
        
        messages_for_llm.append({
            "role": msg.role,
            "content": msg_content if msg.role == "user" else msg.content
        })
    
    try:
        model = request.model or chat.model
        response = await litellm_service.chat_completion(
            api_key=current_user.litellm_key,
            model=model,
            messages=messages_for_llm,
            stream=request.stream
        )
        
        if request.stream:
            assistant_content = ""
            async for data in response:
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    if chunk.get("choices"):
                        delta = chunk["choices"][0].get("delta", {})
                        if delta.get("content"):
                            assistant_content += delta["content"]
                except:
                    pass
            
            assistant_message = Message(
                chat_id=chat_id,
                role="assistant",
                content=assistant_content,
                model=model
            )
        else:
            assistant_content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = response.get("usage", {})
            tokens_used = usage.get("completion_tokens", 0)
            
            assistant_message = Message(
                chat_id=chat_id,
                role="assistant",
                content=assistant_content,
                model=model,
                tokens_used=tokens_used
            )
        
        db.add(assistant_message)
        await db.commit()
        await db.refresh(assistant_message)
        
        return {
            "user_message": {
                "id": str(user_message.id),
                "role": "user",
                "content": user_message.content,
                "created_at": user_message.created_at.isoformat() if user_message.created_at else None
            },
            "assistant_message": {
                "id": str(assistant_message.id),
                "role": "assistant",
                "content": assistant_message.content,
                "model": assistant_message.model,
                "tokens_used": assistant_message.tokens_used,
                "created_at": assistant_message.created_at.isoformat() if assistant_message.created_at else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calling AI: {str(e)}"
        )
