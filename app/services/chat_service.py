from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime

from app.models.chat import ChatRequest, ChatResponse, ConversationHistory, Message
from llm.chains.chat_chains import ChatLearningChain

class ChatService:
    def __init__(self):
        # In-memory storage for conversation histories
        # In production, you would use a database
        self.conversations: Dict[str, ConversationHistory] = {}
        
        # Initialize learning chains for different topics
        self.chains: Dict[str, ChatLearningChain] = {
            "kubernetes": ChatLearningChain(topic="kubernetes"),
            "git": ChatLearningChain(topic="git")
        }
    
    async def process_chat_message(self, request: ChatRequest) -> ChatResponse:
        """Process a user chat message and return the assistant's response"""
        # Get or create conversation
        conversation_id = request.conversation_id
        if not conversation_id or conversation_id not in self.conversations:
            conversation_id = str(uuid.uuid4())
            self.conversations[conversation_id] = ConversationHistory(
                conversation_id=conversation_id,
                topic=request.topic,
                user_id=request.user_id,
                messages=[]
            )
        
        conversation = self.conversations[conversation_id]
        
        # Add user message to conversation history
        user_message = Message(
            role="user",
            content=request.user_message,
            timestamp=datetime.now()
        )
        conversation.messages.append(user_message)
        
        # Get the appropriate chain based on topic
        topic = request.topic.lower()
        if topic not in self.chains:
            assistant_message = "Sorry, I can only help with kubernetes or git topics right now."
        else:
            # Get formatted conversation history
            message_dicts = [
                {"role": msg.role, "content": msg.content} 
                for msg in conversation.messages
            ]
            
            # Process the message
            chain = self.chains[topic]
            assistant_response = chain.process_message(
                request.user_message,
                conversation_history=message_dicts
            )
            
            assistant_message = assistant_response
        
        # Add assistant message to conversation history
        conversation.messages.append(
            Message(
                role="assistant",
                content=assistant_message,
                timestamp=datetime.now()
            )
        )
        conversation.updated_at = datetime.now()
        
        # Create and return response
        return ChatResponse(
            assistant_message=assistant_message,
            conversation_id=conversation_id
        )
    
    async def get_conversation_history(self, conversation_id: str) -> Optional[ConversationHistory]:
        """Get conversation history by ID"""
        return self.conversations.get(conversation_id)
    
    async def introduce_topic(self, conversation_id: str, subtopic: str) -> str:
        """Generate an introduction to a specific subtopic"""
        if conversation_id not in self.conversations:
            return "Conversation not found"
            
        conversation = self.conversations[conversation_id]
        topic = conversation.topic.lower()
        
        if topic not in self.chains:
            return "Topic not supported"
            
        chain = self.chains[topic]
        introduction = chain.introduce_topic(subtopic)
        
        # Add system message to conversation history
        conversation.messages.append(
            Message(
                role="assistant",
                content=introduction,
                timestamp=datetime.now()
            )
        )
        conversation.updated_at = datetime.now()
        
        return introduction