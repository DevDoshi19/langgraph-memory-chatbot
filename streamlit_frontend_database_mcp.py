import queue
import streamlit as st
from langgraph_backend_mcp_async import submit_async_task,chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage ,ToolMessage
import uuid
from langgraph_chatname import name_chat_id

st.title("Hey Dude!!!...")

#------------------------------- utility function --------------------------------

# utility function to generate unique thread id for each new chat session
def generate_thread_id():
    """Generate a unique thread ID as a string"""
    return str(uuid.uuid4())

def reset_chat():
    """Create a new chat thread and reset message history"""
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['message_history'] = []
    
    # Add new thread to the list
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)
    
    # DON'T set initial title here - let it generate after first message
    # Force UI refresh
    st.rerun()

def add_thread_id(thread_id):
    """Add thread ID to chat history if not already present"""
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def load_coversation(thread_id):
    """Load conversation history for a given thread"""
    try:
        state = chatbot.get_state(
            config={"configurable": {"thread_id": thread_id}}
        )

        if not state or "messages" not in state.values:
            return []

        return state.values["messages"]
    except Exception as e:
        print(f"Error loading conversation: {e}")
        return []

def generate_chat_title(thread_id):
    """Generate or retrieve chat title for a thread"""
    messages = load_coversation(thread_id)
    
    if messages and len(messages) > 0:
        try:
            # Get first 2 messages for title generation
            msg_text = []
            for m in messages[:2]:
                if hasattr(m, 'content') and m.content:
                    msg_text.append(str(m.content))
            
            if msg_text:
                title = name_chat_id(thread_id, msg_text)
                return str(title)
            else:
                return "New Chat"
        except Exception as e:
            print(f"Error generating title for {thread_id}: {e}")
            return "New Chat"
    else:
        return "New Chat"

#------------------------------- session state initialization --------------------------------

# Initialize all session state variables
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
    
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = retrieve_all_threads()

if "chat_titles" not in st.session_state:
    st.session_state["chat_titles"] = {}
    
# Add current thread to chat list
add_thread_id(st.session_state['thread_id'])

# Update config with current thread_id
CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

#----------------------------------- sidebar ------------------------------------
st.sidebar.title("Multicapable Chatbot")

if st.sidebar.button('New Chat', use_container_width=True):
    reset_chat()
    
st.sidebar.subheader("Chat History")

# Display chat threads in reverse order (newest first)
for thread_id in st.session_state['chat_thread'][::-1]:
    
    # Generate title - check if it needs regeneration
    messages = load_coversation(thread_id)
    
    # If no title exists OR if title is "New Chat" but messages exist, generate new title
    if thread_id not in st.session_state["chat_titles"]:
        st.session_state["chat_titles"][thread_id] = generate_chat_title(thread_id)
    elif st.session_state["chat_titles"][thread_id] == "New Chat" and messages and len(messages) > 0:
        # Regenerate title if it's still "New Chat" but conversation has started
        st.session_state["chat_titles"][thread_id] = generate_chat_title(thread_id)

    # Get the chat title
    chat_title = st.session_state["chat_titles"][thread_id]
    
    # Highlight the current active chat
    is_current = (thread_id == st.session_state['thread_id'])
    button_type = "primary" if is_current else "secondary"

    # Create button for each chat
    if st.sidebar.button(
        chat_title, 
        key=f"chat_{thread_id}",
        use_container_width=True,
        type=button_type
    ):
        # Switch to selected chat
        st.session_state['thread_id'] = thread_id
        
        # Load conversation history
        messages = load_coversation(thread_id)

        # Convert to message history format
        temp_message_history = []
        for message in messages:
            if isinstance(message, HumanMessage):
                temp_message_history.append({'role': 'user', 'content': message.content})
            elif isinstance(message, AIMessage):
                temp_message_history.append({'role': 'assistant', 'content': message.content})

        st.session_state['message_history'] = temp_message_history
        
        # Refresh the page to show the selected chat
        st.rerun()
        
#---------------------------------- main page -----------------------------------

# Display chat history
for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")
if user_input:
    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    st.session_state['message_history'].append({'role': 'user', 'content': user_input})

    with st.chat_message('user'):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        status_holder = {"box": None}

        def ai_only_stream():
            event_queue = queue.Queue()

            async def run_stream():
                try:
                    async for message_chunk, metadata in chatbot.astream(
                        {"messages": [HumanMessage(content=user_input)]},
                        config=CONFIG,
                        stream_mode="messages",
                    ):
                        event_queue.put((message_chunk, metadata))
                except Exception as exc:
                    event_queue.put(("error", exc))
                finally:
                    event_queue.put(None)

            # Submit async task OUTSIDE of run_stream
            submit_async_task(run_stream())

            while True:
                item = event_queue.get()
                if item is None:
                    break

                message_chunk, metadata = item

                if message_chunk == "error":
                    raise metadata

                # Show tool status when a tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Yield only assistant tokens
                if isinstance(message_chunk, AIMessage) and message_chunk.content:
                    yield message_chunk.content

        try:
            ai_message = st.write_stream(ai_only_stream())

            # Finalize tool status box if it was used
            if status_holder["box"] is not None:
                status_holder["box"].update(
                    label="✅ Tool finished", state="complete", expanded=False
                )

            # Save assistant message
            st.session_state['message_history'].append(
                {'role': 'assistant', 'content': ai_message}
            )

            # Regenerate chat title after first exchange
            current_thread = st.session_state['thread_id']
            if st.session_state["chat_titles"].get(current_thread) == "New Chat":
                st.session_state["chat_titles"][current_thread] = generate_chat_title(current_thread)

        except Exception as e:
            st.error(f"Error getting response: {e}")