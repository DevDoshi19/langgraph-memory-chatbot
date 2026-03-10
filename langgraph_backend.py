from langgraph.graph import StateGraph ,START, END
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage ,HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict ,Annotated
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.7)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
def chat_node(state: ChatState) -> str:
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# for meassage_chunk,metadata in chatbot.stream(
#     {"messages": [HumanMessage(content="can you give me recipe for pasta?")]},
#     config={"configurable": {"thread_id": "thread-1"}},
#     stream_mode="messages"
# ):
#     if meassage_chunk:
#         print(meassage_chunk.content,end="",flush=True)
        
# print(type(stream)) Generator 
