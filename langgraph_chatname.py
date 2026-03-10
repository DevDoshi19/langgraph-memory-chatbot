from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import List

class NameChatState(BaseModel):
    name_of_chat: str = Field(
        ...,
        description="Short chat title in 2-3 words, no punctuation, no quotes"
    )

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7
)

structured_llm = llm.with_structured_output(NameChatState)

def name_chat_id(thread_id: str, messages: List[str]) -> str:
    """Generate a short title for a chat conversation"""
    
    # Handle empty messages
    if not messages or len(messages) == 0:
        return "New Chat"
    
    # Join first few messages
    conversation_text = "\n".join(str(msg) for msg in messages[:4] if msg)
    
    # Limit text length to avoid token limits
    if len(conversation_text) > 500:
        conversation_text = conversation_text[:500]
    
    try:
        response = structured_llm.invoke(
            f"""Generate a short chat title (2-3 words only).
                Rules:
                - Maximum 3 words
                - No punctuation marks
                - No quotes
                - Descriptive of the topic

                Conversation:
                {conversation_text}

                Examples: "Python Tutorial", "Recipe Ideas", "Travel Planning"
                """
            )
        
        title = response.name_of_chat.strip()
        
        # Clean up the title
        title = title.replace('"', '').replace("'", '').replace('.', '').replace(',', '')
        
        # Limit to 30 characters
        if len(title) > 30:
            title = title[:30].strip()
        
        return title if title else "New Chat"
        
    except Exception as e:
        print(f"Error generating chat name: {e}")
        return "New Chat"