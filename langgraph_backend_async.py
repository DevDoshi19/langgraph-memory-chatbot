from urllib import response
from langgraph.graph import StateGraph ,START, END
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage ,HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict ,Annotated
from dotenv import load_dotenv
import sqlite3
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
import requests
import os
import asyncio 

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.7)

#--------------- tools -------------------

# Define a tool for DuckDuckGo search
search_tool = DuckDuckGoSearchRun(regoin="us", safesearch="Moderate")

@tool
def calculator(first_number: float, second_number: float, operation: str) -> dict:
    """A simple calculator tool that performs basic arithmetic operations."""
    if operation == "add":
        result = first_number + second_number
    elif operation == "subtract":
        result = first_number - second_number
    elif operation == "multiply":
        result = first_number * second_number
    elif operation == "divide":
        if second_number == 0:
            return {"error": "Cannot divide by zero"}
        result = first_number / second_number
    else:
        return {"error": "Invalid operation. Supported operations are add, subtract, multiply, divide."}
    
    return {"result": result}

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=8IXFN47U44T61I85"
    r = requests.get(url)
    return r.json()

@tool
def get_weather_data(city: str) -> str:
    """
    This function fetches the current weather data for a given city
    """
    url = f'https://api.weatherstack.com/current?access_key=59d7a1adfb6dca7086d08fcdc620cfc0&query={city}'

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Could not fetch weather data for {city}. Please try again later."}
    
# make a list of tools 
tools = [search_tool, calculator, get_stock_price, get_weather_data]

# make the llm tool-aware
llm_with_tools = llm.bind_tools(tools)

#-------------------------------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
def build_graph():
    
    async def chat_node(state: ChatState) -> str:
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    # conn = sqlite3.connect(database="/tmp/chat_history.db", check_same_thread=False)
    # checkpointer = SqliteSaver(conn=conn)


    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge('tools', 'chat_node')

    chatbot = graph.compile()  # Removed checkpointer since it's commented out
    
    return chatbot 

async def main():
    
    chatbot = build_graph()
    
    
    result = await chatbot.ainvoke({"messages": [HumanMessage(content="Hi how are you ?")]})
    print(result["messages"][-1].content)
    
if __name__ == "__main__":
    asyncio.run(main())
    