import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit_plotly_events import plotly_events
from redditsearch.engine import search
from redditsearch.misc.data_models import Query

#Search bar
st.title("Reddit Post Search and Summary")
query = st.text_input("Enter your search query:", "")

if query:
    # 2. Call the backend function with the query
    payload = Query(query=query, maxposts=7)
    response = search(payload)

    # 3. Display the text summary
    st.subheader("Summary")
    st.write(response.summary)

    #Create DF
    df = pd.DataFrame(response.keyword_frequencies)
    # Create bar plot
    fig = px.bar(df, x='', y='No. of mentions', title=query)
    

    # Display the plot and enable events
    selected_points = plotly_events(fig, click_event=True)

    # Display top comments when a bar is clicked
    if selected_points:
        selection = selected_points[0]['x']

        disp_df = response.comments_data[
                    response.comments_data[selection] == 1]['content']

        st.dataframe(disp_df,
                    hide_index=True
                    )