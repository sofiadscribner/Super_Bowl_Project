# load packages

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

with tab2:
    input = st.radio('Select a marketing metric.', ['Brand Awareness','Brand Familiarity',  'Brand Momentum', 'Consideration of Purchasing','Perception of Quality'])
    metric_map = {
            'Brand Awareness': 'awareness_increase',
            'Brand Familiarity': 'familiarity_increase',
            'Brand Momentum': 'momentum_increase',
            'Consideration of Purchasing': 'consideration_increase',
            'Perception of Quality': 'quality_increase'
        }
    
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

with tab3:
    df_table = df[['Advertiser/product', 'Likes', 'Views']].copy().dropna()
    df_table['like_to_view_ratio'] = (df_table['Likes'] / df_table['Views']) * 100
    df_table['like_to_view_ratio'] = df_table['like_to_view_ratio'].round(2)

    selection = st.selectbox('Sort by:', ['Likes', 'Views', 'Like-to-View-Ratio'])

    if selection == 'Likes':
        sort_by = 'Likes'
    elif selection == 'Views':
        sort_by = 'Views'
     elif selection == 'Likes':
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

    fig.update_layout(title='Youtube Engagement Table')
    st.plotly_chart(fig, use_container_width=True)
