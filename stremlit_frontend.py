import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

# st.session_state -> dict -> 
CONFIG = {'configurable': {'thread_id': 'thread-1'}}

st.title("Chat with chatbot")

# st.session_state is used to store the message history across different interactions with the chatbot.
# it is also dict like object that can store any data we want to persist across different interactions with the chatbot.
# it only remains in memory for the duration of the user's session, and it is not shared across different users or sessions.
# after reloading the page, the message history will be lost and the chatbot will start fresh without any previous context.
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

#loading message history from session state
for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Type your message here...")

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
    
    ai_message = response['messages'][-1].content
    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)