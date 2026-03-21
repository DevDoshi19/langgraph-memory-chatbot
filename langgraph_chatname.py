# from langchain_groq import ChatGroq
# from pydantic import BaseModel, Field
# from typing import List

# class NameChatState(BaseModel):
#     name_of_chat: str = Field(
#         ...,
#         description="Short chat title in 2-3 words, no punctuation, no quotes"
#     )

# llm = ChatGroq(
#     model="openai/gpt-oss-120b",
#     temperature=0.7
# )

# structured_llm = llm.with_structured_output(NameChatState)

# def name_chat_id(thread_id: str, messages: List[str]) -> str:
#     """Generate a short title for a chat conversation"""
    
#     # Handle empty messages
#     if not messages or len(messages) == 0:
#         return "New Chat"
    
#     # Join first few messages
#     conversation_text = "\n".join(str(msg) for msg in messages[:4] if msg)
    
#     # Limit text length to avoid token limits
#     if len(conversation_text) > 500:
#         conversation_text = conversation_text[:500]
    
#     try:
#         response = structured_llm.invoke(
#             f"""Generate a short chat title (2-3 words only).
#                 Rules:
#                 - Maximum 3 words
#                 - No punctuation marks
#                 - No quotes
#                 - Descriptive of the topic

#                 Conversation:
#                 {conversation_text}

#                 Examples: "Python Tutorial", "Recipe Ideas", "Travel Planning"
#                 """
#             )
        
#         title = response.name_of_chat.strip()
        
#         # Clean up the title
#         title = title.replace('"', '').replace("'", '').replace('.', '').replace(',', '')
        
#         # Limit to 30 characters
#         if len(title) > 30:
#             title = title[:30].strip()
        
#         return title if title else "New Chat"
        
#     except Exception as e:
#         print(f"Error generating chat name: {e}")
#         return "New Chat"

# langgraph_chatname.py

from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# Plain LLM — no tools, no structured output, no tool_choice
_name_llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.3)

def name_chat_id(thread_id: str, messages: list) -> str:
    """Generate a short 2-3 word title for a chat conversation."""
    
    if not messages:
        return "New Chat"
    
    try:
        preview = " ".join(str(m) for m in messages[:2] if m)[:300]
        
        response = _name_llm.invoke(
            f"Give a 2-3 word title for this chat. "
            f"No quotes, no punctuation, just the words.\n\n"
            f"Chat: {preview}\n\n"
            f"Title:"
        )
        
        title = (
            response.content
            .strip()
            .replace('"', '')
            .replace("'", '')
            .split('\n')[0]
            [:30]
        )
        
        return title if title else "New Chat"
    
    except Exception as e:
        print(f"Error generating chat name: {e}")
        return "New Chat"