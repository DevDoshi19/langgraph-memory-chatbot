import os
from urllib import response
from langgraph.graph import StateGraph ,START, END
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage ,HumanMessage
from langgraph.graph.message import add_messages
from typing import TypedDict ,Annotated
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_core.tools import tool
import asyncio 
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.7)

#MCP client setup
client = MultiServerMCPClient({
    "expense": {
            "transport": "streamable_http",  # if this fails, try "sse"
            "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
        }
})
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
async def build_graph():
    
    tools = await client.get_tools()
    
    llm_with_tools = llm.bind_tools(tools)
    
    async def chat_node(state: ChatState) -> str:
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge('tools', 'chat_node')

    chatbot = graph.compile()  # Removed checkpointer since it's commented out
    
    return chatbot 

async def main():
    
    chatbot = await build_graph()
    
    
    result = await chatbot.ainvoke({"messages": [HumanMessage(content="add expense of 50 ruppes for groceries")]})
    print(result["messages"][-1].content)
    
if __name__ == "__main__":
    asyncio.run(main())
 