# from langchain_groq import ChatGroq
# from langgraph.graph import StateGraph ,START, END
# from langchain_core.messages import BaseMessage ,HumanMessage
# from langgraph.graph.message import add_messages
# from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
# from langgraph.prebuilt import ToolNode,tools_condition
# from langchain_community.tools import DuckDuckGoSearchRun
# from langchain_core.tools import tool , BaseTool
# from langchain_mcp_adapters.client import MultiServerMCPClient
# from urllib import response
# from typing import TypedDict ,Annotated
# from dotenv import load_dotenv
# import threading
# import sqlite3
# import asyncio
# import aiosqlite
# import requests
# import os

# load_dotenv()

# # Dedicated async loop for backend tasks
# _ASYNC_LOOP = asyncio.new_event_loop()
# _ASYNC_THREAD = threading.Thread(target=_ASYNC_LOOP.run_forever, daemon=True)
# _ASYNC_THREAD.start()


# def _submit_async(coro):
#     return asyncio.run_coroutine_threadsafe(coro, _ASYNC_LOOP)


# def run_async(coro):
#     return _submit_async(coro).result()


# def submit_async_task(coro):
#     """Schedule a coroutine on the backend event loop."""
#     return _submit_async(coro)

# llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.7)

# #--------------- tools -------------------

# search_tool = DuckDuckGoSearchRun(regoin="us", safesearch="Moderate")

# @tool
# def calculator(first_number: float, second_number: float, operation: str) -> dict:
#     """A simple calculator tool that performs basic arithmetic operations."""
#     if operation == "add":
#         result = first_number + second_number
#     elif operation == "subtract":
#         result = first_number - second_number
#     elif operation == "multiply":
#         result = first_number * second_number
#     elif operation == "divide":
#         if second_number == 0:
#             return {"error": "Cannot divide by zero"}
#         result = first_number / second_number
#     else:
#         return {"error": "Invalid operation. Supported operations are add, subtract, multiply, divide."}
    
#     return {"result": result}

# @tool
# def get_stock_price(symbol: str) -> dict:
#     """
#     Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
#     using Alpha Vantage with API key in the URL.
#     """
#     url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=8IXFN47U44T61I85"
#     r = requests.get(url)
#     return r.json()

# @tool
# def get_weather_data(city: str) -> str:
#     """
#     This function fetches the current weather data for a given city
#     """
#     url = f'https://api.weatherstack.com/current?access_key=59d7a1adfb6dca7086d08fcdc620cfc0&query={city}'

#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return {"error": f"Could not fetch weather data for {city}. Please try again later."}
    
# client = MultiServerMCPClient({
#     "expense": {
#             "transport": "streamable_http",  # if this fails, try "sse"
#             "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
#         },
#     "fetch": {
#         "transport": "stdio",
#         "command": "uvx",
#         "args": ["mcp-server-fetch"]
#     },
#     "memory": {
#         "transport": "stdio",
#         "command": "npx",
#         "args": ["-y", "@modelcontextprotocol/server-memory"]
#     },
#     "filesystem": {
#         "transport": "stdio",
#         "command": "npx",
#         "args": [
#             "-y",
#             "@modelcontextprotocol/server-filesystem",
#             "C:/Users/devdo/OneDrive/Desktop"  # restrict to this folder
#         ]
#     }
# })

# def load_mcp_tools()-> list[BaseTool]:
#     """Load tools from MCP and bind them to the LLM."""
#     try:
#         return run_async(client.get_tools())
#     except Exception :
#         return []

# mcp_tools = load_mcp_tools()

# tools = [search_tool, calculator, get_stock_price, get_weather_data] + mcp_tools

# llm_with_tools = llm.bind_tools(tools) if tools else llm

# #-------------------------------------------
# class ChatState(TypedDict):
#     messages: Annotated[list[BaseMessage], add_messages]
    
# async def chat_node(state: ChatState) -> str:
#     messages = state["messages"]
#     response = await llm_with_tools.ainvoke(messages)
#     return {"messages": [response]}

# tool_node = ToolNode(tools)

# DB_PATH = os.path.join(os.path.dirname(__file__), "chat_history.db")

# async def _init_checkpointer():
#     conn = await aiosqlite.connect(database=DB_PATH, check_same_thread=False)
#     return AsyncSqliteSaver(conn=conn)

# checkpointer = run_async(_init_checkpointer())

# graph = StateGraph(ChatState)

# graph.add_node("chat_node", chat_node)
# graph.add_node("tools", tool_node)

# graph.add_edge(START, "chat_node")
# graph.add_conditional_edges("chat_node",tools_condition)
# graph.add_edge('tools', 'chat_node')

# chatbot = graph.compile(checkpointer=checkpointer)

# async def _alist_thread_ids():
#     """Async helper to retrieve all unique thread IDs"""
#     threads = set()
    
#     try:
#         async for checkpoint in checkpointer.alist(None):
#             config = checkpoint.config
#             if config and 'configurable' in config and 'thread_id' in config['configurable']:
#                 threads.add(config['configurable']['thread_id'])
                
#     except Exception as e:
#         print(f"Error retrieving thread IDs: {e}")
        
#     return list(threads)

# def retrieve_all_threads():
#     """Sync wrapper — safe to call from Streamlit"""
#     return run_async(_alist_thread_ids())

from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, trim_messages
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool, BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import threading
import asyncio
import aiosqlite
import requests
import os

load_dotenv()

# Dedicated async loop for backend tasks
_ASYNC_LOOP = asyncio.new_event_loop()
_ASYNC_THREAD = threading.Thread(target=_ASYNC_LOOP.run_forever, daemon=True)
_ASYNC_THREAD.start()

def _submit_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, _ASYNC_LOOP)

def run_async(coro):
    return _submit_async(coro).result()

def submit_async_task(coro):
    return _submit_async(coro)

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.7)

# --------------- tools -------------------

search_tool = DuckDuckGoSearchRun(region="us", safesearch="Moderate")

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
        return {"error": "Invalid operation. Supported: add, subtract, multiply, divide."}
    return {"result": result}

@tool
def get_stock_price(symbol: str) -> dict:
    """Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA')."""
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=8IXFN47U44T61I85"
    r = requests.get(url)
    return r.json()

@tool
def get_weather_data(city: str) -> str:
    """Fetch the current weather data for a given city."""
    url = f"https://api.weatherstack.com/current?access_key=59d7a1adfb6dca7086d08fcdc620cfc0&query={city}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {"error": f"Could not fetch weather data for {city}. Please try again later."}

client = MultiServerMCPClient({
    "expense": {
        "transport": "streamable_http",
        "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
    },
    "fetch": {
        "transport": "stdio",
        "command": "uvx",
        "args": ["mcp-server-fetch"]
    },
    "memory": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "filesystem": {
        "transport": "stdio",
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-filesystem",
            "C:/Users/devdo/OneDrive/Desktop"
        ]
    }
})

def load_mcp_tools() -> list[BaseTool]:
    try:
        return run_async(client.get_tools())
    except Exception as e:
        print(f"MCP tools failed to load: {e}")
        return []

mcp_tools = load_mcp_tools()

tools = [search_tool, calculator, get_stock_price, get_weather_data] + mcp_tools

llm_with_tools = llm.bind_tools(tools) if tools else llm

# --------------- token trimming -------------------

def trim_chat_history(messages: list, max_tokens: int = 5500) -> list:
    """Trim messages to stay within token limit, keeping most recent context."""
    try:
        return trim_messages(
            messages,
            max_tokens=max_tokens,
            token_counter=llm,
            strategy="last",
            start_on="human",
            include_system=True,
            allow_partial=False,
        )
    except Exception:
        # Fallback: keep only last 6 messages if trim_messages fails
        return messages[-6:] if len(messages) > 6 else messages

# --------------- graph -------------------

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

async def chat_node(state: ChatState):
    messages = trim_chat_history(state["messages"])   # ← trim here
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_history.db")

async def _init_checkpointer():
    conn = await aiosqlite.connect(database=DB_PATH)
    return AsyncSqliteSaver(conn=conn)

checkpointer = run_async(_init_checkpointer())

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)
graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

chatbot = graph.compile(checkpointer=checkpointer)

# --------------- helpers -------------------

async def _alist_thread_ids():
    threads = set()
    try:
        async for checkpoint in checkpointer.alist(None):
            config = checkpoint.config
            if config and "configurable" in config and "thread_id" in config["configurable"]:
                threads.add(config["configurable"]["thread_id"])
    except Exception as e:
        print(f"Error retrieving thread IDs: {e}")
    return list(threads)

def retrieve_all_threads():
    return run_async(_alist_thread_ids())
