import streamlit as st

st.title("Settings")
    
# Add new feed
st.header("Feed Management")
new_source = st.text_input("Add new RSS feed URL")
sources = st.session_state.ragfeed.getSources()
if st.button("Add Source") and new_feed:
    if new_source not in sources:
        st.session_state.feeds.append(new_source)
        st.success(f"Added: {new_source}")
    else:
        st.warning("Feed already exists!")

# Display and manage existing feeds
st.subheader("Your Sources")
for source in sources:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text(f"{source["title"]}") #TODO: Filter on click
    with col2:
        st.text(f"-") #TODO: Unread
