from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from typing import Dict, Any, List, Optional
import json
import os

from llm.prompts.chat_prompts import (
    KUBERNETES_TEACHER_PROMPT, 
    GIT_TEACHER_PROMPT,
    TOPIC_INTRODUCTION_PROMPT,
    LEARNING_ASSESSMENT_PROMPT
)

class ChatLearningChain:
    def __init__(self, topic: str = "kubernetes"):
        self.llm = ChatOpenAI(
            model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4"),
            temperature=0.7
        )
        self.topic = topic.lower()
        self.memory = ConversationBufferMemory(
            memory_key="conversation_history",
            input_key="user_message"
        )
        
        # Select the appropriate prompt based on topic
        if self.topic == "kubernetes":
            self.prompt = KUBERNETES_TEACHER_PROMPT
        elif self.topic == "git":
            self.prompt = GIT_TEACHER_PROMPT
        else:
            raise ValueError(f"Unsupported topic: {topic}")
            
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
            verbose=True
        )
        
        # Track learning progress
        self.experience_level = "beginner"
        self.concepts_covered = []
        self.current_focus = "introduction"
        
    def format_conversation_history(self, messages: List[Dict[str, Any]]) -> str:
        """Format message history for prompt context"""
        formatted = ""
        for msg in messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            formatted += f"{role}: {content}\n\n"
        return formatted
        
    def process_message(self, 
                        user_message: str, 
                        conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """Process a user message and return the assistant's response"""
        # Use provided conversation history or the chain's memory
        if conversation_history:
            formatted_history = self.format_conversation_history(conversation_history)
        else:
            formatted_history = self.memory.buffer
            
        # Prepare inputs for the chain
        inputs = {
            "user_message": user_message,
            "conversation_history": formatted_history,
            "experience_level": self.experience_level,
            "concepts_covered": ", ".join(self.concepts_covered) if self.concepts_covered else "none",
            "current_focus": self.current_focus
        }
        
        # Get response from the chain
        response = self.chain.invoke(inputs)
        
        # Update the memory if using custom conversation history
        if conversation_history:
            self.memory.chat_memory.add_user_message(user_message)
            self.memory.chat_memory.add_ai_message(response["text"])
            
        # Extract and update learning progress (simplified)
        # In a real implementation, this would use a separate chain to analyze understanding
        if len(self.memory.buffer) > 500:  # Some arbitrary threshold
            self._update_learning_progress()
            
        return response["text"]
    
    def introduce_topic(self, subtopic: str) -> str:
        """Generate an introduction to a new topic or subtopic"""
        intro_chain = LLMChain(
            llm=self.llm,
            prompt=TOPIC_INTRODUCTION_PROMPT
        )
        
        response = intro_chain.invoke({
            "topic": self.topic,
            "subtopic": subtopic
        })
        
        # Update learning tracking
        self.current_focus = subtopic
        self.concepts_covered.append(subtopic)
        
        return response["text"]
    
    def _update_learning_progress(self) -> None:
        """Analyze conversation to update user's learning progress"""
        assessment_chain = LLMChain(
            llm=self.llm,
            prompt=LEARNING_ASSESSMENT_PROMPT
        )
        
        response = assessment_chain.invoke({
            "topic": self.topic,
            "conversation_history": self.memory.buffer
        })
        
        # This would ideally parse the response to update learning progress
        # For now, we just increment the experience level after some interactions
        if len(self.concepts_covered) > 3 and self.experience_level == "beginner":
            self.experience_level = "intermediate"
        elif len(self.concepts_covered) > 7 and self.experience_level == "intermediate":
            self.experience_level = "advanced"