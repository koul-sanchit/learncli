from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatRequest(BaseModel):
    user_message: str
    topic: str  # "kubernetes" or "git"
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    assistant_message: str
    conversation_id: str
    
class LearningTopic(str, Enum):
    KUBERNETES = "kubernetes"
    GIT = "git"
    
class ConversationHistory(BaseModel):
    conversation_id: str
    topic: LearningTopic
    user_id: Optional[str] = None
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)