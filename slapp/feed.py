import streamlit as st
from datetime import datetime
import time

sources = feed = topics = []
if "ragfeed" in st.session_state.keys():
    sources = st.session_state.ragfeed.getSources()
    feed = st.session_state.ragfeed.getArticles()
    topics = st.session_state.ragfeed.getTopTopics()

# Sidebar 
with st.sidebar:
    st.header("Sources:")
    with st.container(height=200, border=False):
        for source in sources:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"{source["title"]}") #TODO: Filter on click
            with col2:
                st.text(f"0") #TODO: Unread

    st.divider()
    if topics:
        st.header("Trending Topics:")
        with st.container(height=200, border=False):
            sel_topic = st.pills(label="Trending Topics", label_visibility="collapsed", options=topics.keys(), key="top_topics", selection_mode="single")
        st.divider()

    # Auto-refresh logic
    if st.session_state.refresh_interval:
        refresh_sec = st.session_state.refresh_interval * 60
               
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

    if st.button("Refresh Now"):
        st.session_state.ragfeed.updateSources()
        st.rerun()

qp = st.query_params.to_dict()
if qp:
    st.text(qp['tab'])

# App title
st.title("📰 RagFeed")

# Collect all entries
all_entries = []

if topics and sel_topic != None:
    st.header(topics[sel_topic]["title"])
    st.write(topics[sel_topic]["summary"])
    for article in topics[sel_topic]["articles"]:          
        # Display entry
        st.markdown(f"""
        <div class="feed-item">
            <div class="feed-title">{article["title"]}</div>
            <div class="feed-date">{datetime.fromtimestamp(article["pub_date"]).strftime('%a, %d %b %Y %H:%M')}</div>
            <div class="feed-summary">{article["description"][:300]}{'...' if len(article["description"]) > 300 else ''}</div>
            <a href="{article["link"]}" target="_blank">Read more</a>
        </div>
        """, unsafe_allow_html=True)
else:
    # Display feeds
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

