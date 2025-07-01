import streamlit as st
from datetime import datetime

# Get Content from backend
sources = feed = topics = []
if "ragfeed" in st.session_state.keys():
    st.session_state.ragsearches = st.session_state.ragfeed.getRagSearches()

# Page Methods
def set_search(rsearch):
    st.session_state.sel_search = rsearch

def add_ragsearch(search):
    response = st.session_state.ragfeed.askRag(search)
    if response:
        st.session_state.ragsearches.append(response)
        set_search(response)
    else:
        st.warning("I was unable to do the search, please try again.", width="stretch")


def del_ragsearch(rsearch):
    st.session_state.ragfeed.delRagSearch(rsearch["title"])
    if rsearch == st.session_state.sel_search:
        del st.session_state.sel_search
    else:
        st.session_state.ragsearches = st.session_state.ragfeed.getRagSearches()


# Sidebar 
with st.sidebar:
    # Section to Add Searches
    col_search, col_search_btn = st.columns([3, 1])
    with col_search:
        search = st.text_input(label="Add Search", label_visibility="collapsed", placeholder= "Add Search")
    with col_search_btn:
        btn_search = st.button(":material/search:")

    searches = [rsearch["title"] for rsearch in st.session_state.ragsearches]
    if btn_search and search:
        if search not in searches:
            searches.append(search)
            with st.spinner("Searching Articles..."):
                add_ragsearch(search)
        else:
            for rsearch in st.session_state.ragsearches:
                if rsearch["title"] == search:
                    set_search(rsearch)
                    break

    if st.session_state.ragsearches:
        st.divider()

        st.header("Your searches:")
        # Section with saved searches
        col_list_btn, col_list  = st.columns([1, 9])
        for rsearch in st.session_state.ragsearches:
            with col_list_btn:
                st.button(label=":material/delete:", key="rm_" + rsearch["title"], on_click=del_ragsearch, args=[rsearch], type="tertiary")
            with col_list:
                st.button(label=rsearch["title"], key="link_" + rsearch["title"] , on_click=set_search, args=[rsearch], type="tertiary")
        

if "sel_search" in st.session_state.keys():
    sel_search = st.session_state.sel_search 
    
    # Section Title
    st.title(":material/contact_support: " + sel_search["title"])

    st.write(sel_search["summary"])
    for article in sel_search["articles"]:          
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
    # Section Title
    st.title(":material/contact_support: Ask Feed")

    st.write("Ask me about a topic you want to track.")
    st.write("I'll search related articles into your sources and keep the search updated when new articles are published.")


