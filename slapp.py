# Setup RagFeed
from RagFeed import RagFeed
ragfeed = RagFeed()

import streamlit as st

from datetime import datetime
import time

# Set page config
st.set_page_config(
    page_title="RSS Feed Reader",
    page_icon="📰",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .feed-item {
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        background-color: rgb(38, 39, 48);
    }
    .feed-title {
        font-weight: bold;
        font-size: 18px;
    }
    .feed-date {
        color: #606060;
        font-size: 14px;
    }
    .feed-summary {
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.title("📰 RagFeed")

# Sidebar for feed management
with st.sidebar:
    st.header("Feed Management")
    
    # Add new feed
    new_source = st.text_input("Add new RSS feed URL")
    if st.button("Add Source") and new_feed:
        if new_source not in st.session_state.sources:
            st.session_state.feeds.append(new_source)
            st.success(f"Added: {new_source}")
        else:
            st.warning("Feed already exists!")
    
    # Display and manage existing feeds
    st.subheader("Your Sources")
    sources = ragfeed.getSources()
    for source in sources:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(f"{source["title"]}") #TODO: Filter on click
        with col2:
            st.text(f"0") #TODO: Unread
    
    # Refresh interval
    st.subheader("Settings")
    refresh_interval = st.slider("Auto-refresh interval (minutes)",  min_value=5, max_value=60, value=15, step=5)
    
    if st.button("Refresh Now"):
        ragfeed.updateSources()
        st.rerun()

# Main content area
tab1, tab2 = st.tabs(["Feed View", "Chat View"])

# Collect all entries
all_entries = []

with tab1:
    # Display feeds
    feed = ragfeed.getArticles()
    for article in feed:          
        # Display entry
        st.markdown(f"""
        <div class="feed-item">
            <div class="feed-title">{article["title"]}</div>
            <div class="feed-date">{datetime.fromtimestamp(article["pub_date"]).strftime('%a, %d %b %Y %H:%M')}</div>
            <div class="feed-summary">{article["description"][:300]}{'...' if len(article["description"]) > 300 else ''}</div>
            <a href="{article["link"]}" target="_blank">Read more</a>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    # Store LLM generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

    # User-provided prompt
    if prompt := st.chat_input(disabled=False):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ragfeed.askRag(prompt, 10)
                placeholder = st.empty()
                full_response = ''
                for item in response:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)

# Footer
st.markdown("---")
# Auto-refresh logic
if refresh_interval:
    refresh_sec = refresh_interval * 60
    st.markdown(f"Page will refresh in {refresh_interval} minutes.")
    
    # Add a placeholder for the countdown
    countdown = st.empty()
    
    # Display time until next refresh
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    elapsed = time.time() - st.session_state.last_refresh
    remaining = max(0, refresh_sec - elapsed)
    
    # Update countdown
    with countdown:
        st.text(f"Next refresh in: {int(remaining // 60)}m {int(remaining % 60)}s")
        
    # Check if it's time to refresh
    if elapsed >= refresh_sec:
        st.session_state.last_refresh = time.time()
        st.rerun()


st.markdown("📰 RSS Feed Reader App • Created with Streamlit") 