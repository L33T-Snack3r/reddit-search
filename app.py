import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit_plotly_events import plotly_events
from redditsearch.engine import search
from redditsearch.misc.data_models import Query
from loguru import logger

# Title and search bar
st.title("Reddit Post Search and Summary")
query = st.text_input("Enter your search query:", "")

# Initialize session state for search results
if "search_results" not in st.session_state:
    st.session_state.search_results = None

# Perform the search only if the query changes
if query and st.button("Search"):
    payload = Query(query=query, maxposts=7)
    response = search(payload)
    st.session_state.search_results = {
        "summary": response.summary,
        "keyword_frequencies": pd.DataFrame(response.keyword_frequencies),
        "comments_data": response.comments_data.copy(),
    }

# Display results if available
if st.session_state.search_results:
    # Display summary
    st.subheader("Summary")
    st.write(st.session_state.search_results["summary"])

    # Create bar plot
    df = st.session_state.search_results["keyword_frequencies"]
    comments_df = st.session_state.search_results["comments_data"]

    fig = px.bar(df, x="keywords", y="mentions", title=query)
    
    # Display the plot and enable events
    selected_points = plotly_events(fig, click_event=True)

    # Display top comments when a bar is clicked
    if selected_points:
        selection = df.iloc[selected_points[0]["pointIndex"]]["keywords"]
        disp_df = comments_df[comments_df[selection] == 1]["content"].rename(selection)
        st.dataframe(disp_df, hide_index=True)