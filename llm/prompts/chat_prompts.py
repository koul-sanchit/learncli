from langchain.prompts import PromptTemplate

# Base teacher prompt for both Kubernetes and Git
TEACHER_BASE_PROMPT = """
You are an expert instructor teaching {topic}. Your goal is to help the user learn through conversation.
Be concise but thorough in your explanations. Use simple language but don't oversimplify concepts.
After explaining a concept, ask a question to check understanding or prompt further discussion.

Current learning context:
- Topic: {topic}
- User's experience level appears to be: {experience_level}
- We've covered: {concepts_covered}
- Current focus: {current_focus}

Previous conversation:
{conversation_history}

User message: {user_message}

Respond in a helpful, engaging way as a teacher. Don't be overly formal - be conversational but professional.
"""

# Kubernetes-specific teacher prompt
KUBERNETES_TEACHER_PROMPT = PromptTemplate(
    input_variables=[
        "experience_level", 
        "concepts_covered", 
        "current_focus", 
        "conversation_history", 
        "user_message"
    ],
    template=TEACHER_BASE_PROMPT.replace("{topic}", "Kubernetes")
)

# Git-specific teacher prompt
GIT_TEACHER_PROMPT = PromptTemplate(
    input_variables=[
        "experience_level", 
        "concepts_covered", 
        "current_focus", 
        "conversation_history", 
        "user_message"
    ],
    template=TEACHER_BASE_PROMPT.replace("{topic}", "Git")
)

# New topic introduction prompt
TOPIC_INTRODUCTION_PROMPT = PromptTemplate(
    input_variables=["topic", "subtopic"],
    template="""
You are introducing a new {topic} concept: {subtopic} to a student.
Provide a brief, engaging introduction to this concept that:
1. Explains what it is in simple terms
2. Highlights why it's important
3. Connects it to concepts they likely already know
4. Ends with a simple question to engage the user

Keep the introduction under 200 words and conversational in tone.
"""
)

# Learning assessment prompt
LEARNING_ASSESSMENT_PROMPT = PromptTemplate(
    input_variables=["topic", "conversation_history"],
    template="""
Based on the conversation below about {topic}, assess the user's understanding.
Identify:
1. Concepts they seem to understand well
2. Concepts they might be struggling with
3. A good next concept to introduce or review

Conversation:
{conversation_history}

Provide your assessment and suggest a good next topic to explore.
"""
)