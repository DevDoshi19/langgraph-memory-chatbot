# streamlit_resmue_chat_frontend.py
import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage , AIMessage
import uuid
from langgraph_chatname import name_chat_id

st.title("Hey Dude!!!...")
#------------------------------- utility function --------------------------------

# utility function to generate unique thread id for each new chat session
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread_id(thread_id)
    st.session_state['message_history'] = []

    st.session_state.setdefault("chat_titles", {})
    st.session_state["chat_titles"][thread_id] = "New Chat"

    
def add_thread_id(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def load_coversation(thread_id):
    state = chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )

    if not state or "messages" not in state.values:
        return []

    return state.values["messages"]

#------------------------------- session state initialization --------------------------------

# st.session_state -> dict -> 
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
    
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = []

if "chat_titles" not in st.session_state:
    st.session_state["chat_titles"] = {}
    
add_thread_id(st.session_state['thread_id'])

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

#----------------------------------- sidebar ------------------------------------
st.sidebar.title("Langgraph Chatbot")
if st.sidebar.button('New Chat'):
    reset_chat()
    
st.sidebar.subheader("Chat History")

# Display chat history
for thread_id in st.session_state['chat_thread'][::-1]:
    # Generate title only once per thread
    if thread_id not in st.session_state["chat_titles"]:
        messages = load_coversation(thread_id)

        if messages and len(messages) > 0:  # Only if conversation exists
            try:
                msg_text = [m.content for m in messages[:2]]
                title = name_chat_id(thread_id, msg_text)
                st.session_state["chat_titles"][thread_id] = str(title)
            except Exception as e:
                print(f"Error generating title: {e}")
                st.session_state["chat_titles"][thread_id] = "New Chat"
        else:
            st.session_state["chat_titles"][thread_id] = "New Chat"

    chat_title = st.session_state["chat_titles"][thread_id]
    
    # Highlight current chat
    is_current = (thread_id == st.session_state['thread_id'])
    button_type = "primary" if is_current else "secondary"

    if st.sidebar.button(
        chat_title, 
        key=f"chat_{thread_id}",
        use_container_width=True,
        type=button_type
    ):
        st.session_state['thread_id'] = thread_id
        messages = load_coversation(thread_id)

        temp_message_history = []
        for message in messages:
            if isinstance(message, HumanMessage):
                temp_message_history.append({'role': 'user', 'content': message.content})
            elif isinstance(message, AIMessage):
                temp_message_history.append({'role': 'assistant', 'content': message.content})

        st.session_state['message_history'] = temp_message_history
        st.rerun()
        
#---------------------------------- main page -----------------------------------

for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Type your message here...")

if user_input:

    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk,metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            )
        )
    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})

# streamlit_resmue_chat_frontend.py