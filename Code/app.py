# load packages

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import kaleido
import streamlit as st
from io import BytesIO
from PIL import Image
import requests

# read in data from github repo

url = 'https://raw.githubusercontent.com/sofiadscribner/Super_Bowl_Project/main/Data/sb_data.csv'

df = pd.read_csv(url)

# initiate streamlit app with title and image

img_url = 'https://raw.githubusercontent.com/sofiadscribner/Super_Bowl_Project/main/Code/logo.png'
response = requests.get(img_url)
image = Image.open(BytesIO(response.content))
col1, col2 = st.columns([5, 3])

with col1:
    st.markdown(
        """
        <h2 style='text-align: center;'>
            Super Bowl 2024 Ads:<br>A Data-Driven Exploration
        </h2>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.image(image, use_container_width=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(['Introduction','YouTube Stats', 'Google Trends', 'Polling Data', 'Celebrity Influence'])

with tab1:
    st.markdown('### Introduction')
    st.markdown('#### Brands spent an estimated $650 million on Super Bowl ads in 2024. Was it worth it?')
    st.markdown('##### Use this app to explore the reach and impact of each ad, and determine which brands won the Big Game.')
    
with tab2:
    st.markdown('### YouTube Stats')
    st.markdown("#### YouTube engagement is an important way to gauge ad reach.")

# what were the top X most viewed superbowl ads on youtube?

    bars_df = df

    bars_df['ad_label'] = bars_df['Title'] + ' - ' + bars_df['Advertiser/product']

# select the top X most viewed Super Bowl ads

    x_ads = st.select_slider('Number of Ads to Display', options=list(range(1, 16)), value=5)
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

# create table for youtube engagement stats

    df_table = df[['Advertiser/product', 'Likes', 'Views']].copy().dropna()
    df_table['like_to_view_ratio'] = (df_table['Likes'] / df_table['Views']) * 100
    df_table['like_to_view_ratio'] = df_table['like_to_view_ratio'].round(2)

# allow user to choose how table is sorted

    selection = st.selectbox('Sort by:', ['Likes', 'Views', 'Like-to-View-Ratio'])

    if selection == 'Likes':
        sort_by = 'Likes'
    elif selection == 'Views':
        sort_by = 'Views'
    elif selection == 'Like-to-View-Ratio':
        sort_by = 'like_to_view_ratio'

    df_table = df_table.sort_values(by= sort_by, ascending=False)

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["Brand", "Likes", "Views", "Like-to-View Ratio (%)"],
            fill_color='red',
            align='center',
            font=dict(color='white', size=14)
        ),
        cells=dict(
            values=[
                df_table['Advertiser/product'],
                df_table['Likes'],
                df_table['Views'],
                df_table['like_to_view_ratio']
            ],
            fill_color='white',
            align='center',
            font=dict(size=12)
        ))
    ])

    fig.update_layout(title='YouTube Engagement Table')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
    "<p style='font-size: 12px; color: gray;'>Data from YouTube, curated <a href='https://github.com/sofiadscribner/Super_Bowl_Project' target='_blank'>here</a>.</p>",
    unsafe_allow_html=True
)
    
# explore google trends data

with tab3:
    st.markdown('### Google Trends')
    st.markdown("#### About 1/5 of the brands experienced their 5-year peak Google search popularity on the week of their Super Bowl Ad.") 
    brands = df['Advertiser/product'].unique()

# allow user to select a brand

    selection = st.selectbox('Select a brand.', sorted(brands), index = 8)
    row = df[df['Advertiser/product'] == selection]
    peaked = row['Peaked'].values[0]

# display whether the brand peaked

    st.markdown(f"#### Did {selection} peak?")
    if peaked:
        st.markdown("<h3 style= 'font-size: 18px; color: green;'>✅ Yes! That brand exerienced their 5-year peak.</h3>", unsafe_allow_html=True)
    else:
        relative_search_popularity = row['Relative_Search_Popularity'].values[0]
        st.markdown(f"<h3 style= 'font-size: 18px; color: red;'>❌ No, but they hit {relative_search_popularity}% of their highest popularity.</h3>", unsafe_allow_html=True)
        
    st.markdown(
        "<p style='font-size: 12px; color: gray;'>Data from Google Trends, curated <a href='https://github.com/sofiadscribner/Super_Bowl_Project' target='_blank'>here</a>.</p>",
        unsafe_allow_html=True)

# create lollipop chart showing marketing metrics 

with tab4:
    st.markdown('### Polling Data')
    st.markdown("#### Marketing polls help determine the immediate effect of the ads on consumer sentiment.")

    input = st.radio('Select a marketing metric.', ['Brand Awareness','Brand Familiarity',  'Brand Momentum', 'Consideration of Purchasing','Perception of Quality'])
    metric_map = {
            'Brand Awareness': 'awareness_increase',
            'Brand Familiarity': 'familiarity_increase',
            'Brand Momentum': 'momentum_increase',
            'Consideration of Purchasing': 'consideration_increase',
            'Perception of Quality': 'quality_increase'
        }
    
    # allow user to select which metric to view

    stat_of_interest = metric_map[input]

    # Filter data
    filtered_df = df[df[stat_of_interest] != 0]

    if filtered_df.empty:
        st.write("No data available for the selected metric!")
    else:
        # Sort and process data
        filtered_df = filtered_df.sort_values(by=stat_of_interest, ascending=False)
        brands = filtered_df['Advertiser/product']
        scores = filtered_df[stat_of_interest]

        fig = go.Figure()
        for i, brand in enumerate(brands):
            fig.add_trace(go.Scatter(
                x=[brand, brand],
                y=[0, scores.iloc[i]],
                mode='lines+markers',
                line=dict(color='gray', width=2),
                marker=dict(size=[0, 15], color='red'),
                showlegend=False,
                name=brand
            ))

        fig.update_layout(
            title=f'Top 10 {input} Increases',
            xaxis_title='Brand',
            yaxis_title= 'Point Increase',
            xaxis_tickangle=-25,
            plot_bgcolor='white',
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            "<p style='font-size: 12px; color: gray;'>Data from The Harris Poll, curated <a href='https://github.com/sofiadscribner/Super_Bowl_Project' target='_blank'>here</a>.</p>",
            unsafe_allow_html=True)
        
with tab5:

    st.markdown('### Celebrity Influence')
    st.markdown("#### Some of the most successful ads, by polling data and by search popularity, included celebrities.")

    # allow user to toggle between YouGov top 10, ads that peaked in google search popularity, and all ads

    toggle = st.segmented_control('Select a group of ads.', ['YouGov Top 10', 'Peaked on Google', 'All'])
    if toggle == 'YouGov Top 10':
        filtered_df = df[df['yougov_ranking'] > 0]
    elif toggle == 'Peaked on Google':
        filtered_df = df[df['Peaked'] == True]
    else:
        filtered_df = df.copy()

    # show how many included celebrities

    celebrity_counts = filtered_df['Celebrity'].value_counts(dropna=False)

    celebrity_counts.index = celebrity_counts.index.map({True: 'Included Celebrity', False: 'No Celebrity'})

    fig = px.pie(celebrity_counts, names=celebrity_counts.index, values=celebrity_counts.values, 
                title='Ads with Celebrities vs. Without Celebrities',
                color_discrete_sequence=['#cc0000','#ffcb8e'])

    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
            "<p style='font-size: 12px; color: gray;'>Data from personal observation and Google Trends, curated <a href='https://github.com/sofiadscribner/Super_Bowl_Project' target='_blank'>here</a>.</p>",
            unsafe_allow_html=True)
