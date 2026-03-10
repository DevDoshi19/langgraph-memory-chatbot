from langgraph.graph import StateGraph ,START, END
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage ,HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict ,Annotated
from dotenv import load_dotenv
import sqlite3

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.7)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
def chat_node(state: ChatState) -> str:
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

conn = sqlite3.connect(database="chat_history.db",check_same_thread=False)

checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)
                                   
                                                                   
# res = chatbot.invoke(
#     {"messages": [HumanMessage(content="can you tell me who is dev doshi ?,who has account name dev_doshi_ and his github profile is DevDoshi19..")]},
#     config={"configurable": {"thread_id": "thread-2"}}
# )

# for i in range(len(res["messages"])):
#     print(res["messages"][i].content)

def retrive_all_thread_ids():
    """Retrieve all unique thread IDs from the database"""
    try:
        threads = set()
        for checkpoint in checkpointer.list(None):
            config = checkpoint.config
            if config and 'configurable' in config and 'thread_id' in config['configurable']:
                threads.add(config['configurable']['thread_id'])
                
        return list(threads)
                
            # same as this but with more checks
            # for chekpoint in checkpointer.list(None):
            #     all_thread.add(chekpoint.config['configurable']['thread_id']) 

    except Exception as e:
        print(f"Error retrieving thread IDs: {e}")
        return []
    
    
# all_thread = set()
# for chekpoint in checkpointer.list(None):
#     all_thread.add(chekpoint.config['configurable']['thread_id'])
    
# print(all_thread)
# checkpointer.list(None)