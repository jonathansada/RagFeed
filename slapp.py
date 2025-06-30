import streamlit as st
from datetime import datetime
import time

if "ragfeed" not in st.session_state.keys():
    from RagFeed import RagFeed
    st.session_state.ragfeed = RagFeed()

sources = feed = topics = []
if "refresh_interval" not in st.session_state.keys():
    # Default refresh interval (TODO: read it from settings)
    st.session_state.refresh_interval = 15

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

    button[kind="topic_link"] {
        background-color: orange;
    }

    button[kind="seondary"] {
        background-color: purple;
    }
</style>
""", unsafe_allow_html=True)




def settings():
    st.title("settings")


pg = st.navigation([
    st.Page("./slapp/feed.py", title="First page", icon="🔥"),
    st.Page("./slapp/rag.py", title="Chat", icon=":material/favorite:"),
    st.Page("./slapp/settings.py", title="Settings", icon=":material/favorite:"),
])
pg.run()