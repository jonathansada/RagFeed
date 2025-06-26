# Setup RagFeed
from RagFeed import RagFeed
import streamlit as st

ragfeed = RagFeed()

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Link Example](https://)"
    "[![GitHub](https://github.com/codespaces/badge.svg)](https://github.com/jonathansada/RagFeed)"

st.title("RagFeed")
st.caption("...")
if "messages" not in st.session_state:
    docs = ragfeed.searchRelated("What are the top 10 most relevant topics for today?")
    for doc in docs:
        st.session_state["messages"] = [{"role": "assistant", "content": doc}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    msg = "hello world"
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

