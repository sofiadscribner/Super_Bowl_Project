# load packages

import numpy as np
import pandas as pd
import plotly.express as px
import kaleido
import streamlit as st


# read in data from github repo

url = 'https://raw.githubusercontent.com/sofiadscribner/Super_Bowl_Project/main/Data/sb_data.csv'

df = pd.read_csv(url)

# initiate streamlit app with title

st.title('Super Bowl 2024 Ads: An Exploration')

tab1, tab2, tab3 = st.tabs(['Youtube Stats', 'Polling Data', 'Celebrity Influence'])

with tab1:
    # what were the top X most viewed superbowl ads on youtube?

    bars_df = df

    bars_df['ad_label'] = bars_df['Title'] + ' - ' + bars_df['Advertiser/product']

    # select the top X most viewed Super Bowl ads

    x_ads = st.select_slider('Number of Ads to Display', options=list(range(1, 16)), value=3)
    top_ads = bars_df.nlargest(x_ads, 'Views').sort_values(by='Views', ascending=True)

    # create a bar chart

    fig = px.bar(
        top_ads, 
        x='Views',
        y='ad_label', 
        title= f'Top {x_ads} Most Viewed Ads on YouTube',
        labels={'ad_label': 'Super Bowl Ad', 'views': 'Total Views'},
        text='Views',  # Display view counts on bars
        color='Views',  # Color based on views
        color_continuous_scale='Reds',
    )

    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(fig, use_container_width=True)