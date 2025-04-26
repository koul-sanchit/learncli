from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

from app.models.chat import ChatRequest, ChatResponse, ConversationHistory
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])

# Dependency to get the chat service
def get_chat_service() -> ChatService:
    return ChatService()

@router.post("/message", response_model=ChatResponse)
async def process_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Process a chat message and return the response"""
    if request.topic.lower() not in ["kubernetes", "git"]:
        raise HTTPException(
            status_code=400,
            detail="Topic must be either 'kubernetes' or 'git'"
        )
    
    response = await chat_service.process_chat_message(request)
    return response

@router.get("/conversation/{conversation_id}", response_model=ConversationHistory)
async def get_conversation(
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get conversation history by ID"""
    conversation = await chat_service.get_conversation_history(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    return conversation

@router.post("/conversation/{conversation_id}/introduce")
async def introduce_topic(
    conversation_id: str,
    subtopic: str = Query(..., description="The subtopic to introduce"),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Generate an introduction to a specific subtopic"""
    conversation = await chat_service.get_conversation_history(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    introduction = await chat_service.introduce_topic(conversation_id, subtopic)
    return {"conversation_id": conversation_id, "introduction": introduction}

@router.get("/topics")
async def get_available_topics():
    """Get list of available learning topics"""
    return {
        "topics": [
            {
                "id": "kubernetes",
                "name": "Kubernetes",
                "subtopics": [
                    "Pods", "Deployments", "Services", "ConfigMaps", 
                    "Secrets", "Namespaces", "RBAC", "Helm"
                ]
            },
            {
                "id": "git",
                "name": "Git",
                "subtopics": [
                    "Basic Workflow", "Branching", "Merging", "Rebasing",
                    "Remote Repositories", "Pull Requests", "Git Hooks",
                    "Advanced Git Commands"
                ]
            }
        ]
    }