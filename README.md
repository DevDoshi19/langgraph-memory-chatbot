# 🤖 LangGraph Chatbot with Tools & SQLite Memory

A conversational AI chatbot built with **LangGraph** and **Streamlit**, featuring persistent multi-session memory, real-time tool use (web search, calculator, stock prices, weather), and an auto-generating chat title sidebar.

---

## 📁 Project Structure

```
├── langgraph_backend_tools.py           # Core LangGraph backend (LLM, tools, graph, memory)
├── streamlit_frontend_database_sqlite.py  # Streamlit frontend (UI, sessions, chat history)
├── langgraph_chatname.py                # Chat title generation module (external dependency)
├── chat_history.db                      # SQLite database (auto-created at runtime)
├── graph_visualization.png              # Auto-generated graph diagram (at runtime)
└── .env                                 # API keys (not committed to version control)
```

---

## ✨ Features

- 🧠 **Persistent Memory** — Chat history saved to SQLite via LangGraph's `SqliteSaver` checkpointer
- 🔀 **Multi-session Support** — Multiple independent chat threads with full conversation history
- 🔧 **Tool-Augmented LLM** — LLM can call tools mid-conversation (web search, calculator, stocks, weather)
- 🏷️ **Auto-generated Chat Titles** — Chat sessions are named intelligently based on conversation content
- ⚡ **Streaming Responses** — Real-time token streaming in the Streamlit UI
- 📊 **Graph Visualization** — LangGraph flow diagram saved automatically as a PNG

---

## 🛠️ Tools Available

| Tool | Description |
|------|-------------|
| `DuckDuckGoSearchRun` | Searches the web for up-to-date information |
| `calculator` | Performs basic arithmetic (add, subtract, multiply, divide) |
| `get_stock_price` | Fetches live stock prices using the Alpha Vantage API |
| `get_weather_data` | Gets current weather for any city using Weatherstack API |

---

## 🏗️ Architecture

```
User Input
    │
    ▼
[chat_node]  ──── tool call? ────►  [tools node]
    ▲                                     │
    └─────────────────────────────────────┘
    │
    ▼
  Output (streamed to UI)
```

The LangGraph graph consists of:
- **`chat_node`** — Calls the LLM (with bound tools) and returns a response
- **`tools`** — Executes any tool the LLM decided to invoke
- **Conditional edge** — Routes back to `chat_node` after tool execution, or ends if no tool call

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2. Install dependencies

```bash
pip install streamlit langgraph langchain langchain-groq langchain-community python-dotenv requests
```

### 3. Configure API keys

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> **Note:** The Alpha Vantage and Weatherstack API keys are currently hardcoded in `langgraph_backend_tools.py`. It is recommended to move these into the `.env` file for security.

### 4. Run the app

```bash
streamlit run streamlit_frontend_database_sqlite.py
```

---

## 🔑 API Keys Required

| Service | Used For | Where to Get |
|---------|----------|--------------|
| **Groq** | LLM inference | [console.groq.com](https://console.groq.com) |
| **Alpha Vantage** | Stock price data | [alphavantage.co](https://www.alphavantage.co) |
| **Weatherstack** | Weather data | [weatherstack.com](https://weatherstack.com) |

---

## 💬 Usage

1. Open the app in your browser (default: `http://localhost:8501`)
2. Type a message in the chat input at the bottom
3. Click **"New Chat"** in the sidebar to start a fresh conversation
4. Previous chat sessions are listed in the sidebar with auto-generated titles — click any to resume

---

## 🗄️ Data Persistence

Chat history is saved to a local SQLite database (`chat_history.db`). This file is created automatically on first run. All threads and messages persist across app restarts.

---

## 📦 Key Dependencies

| Package | Purpose |
|---------|---------|
| `langgraph` | Stateful agent graph orchestration |
| `langchain-groq` | Groq LLM integration |
| `langchain-community` | DuckDuckGo search tool |
| `streamlit` | Web UI framework |
| `sqlite3` | Persistent memory / checkpointing |
| `python-dotenv` | Environment variable management |

---

## ⚠️ Known Limitations

- The `DuckDuckGoSearchRun` region parameter uses `regoin` (typo in source) — this may default to global search
- Alpha Vantage free tier has rate limits (5 requests/min, 500/day)
- The `langgraph_chatname` module is required but not included — ensure it is present before running