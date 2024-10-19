import streamlit as st
import pandas as pd
from instagram_analyzer import analyze_instagram_profile
from content_generator import generate_content_plan
from strategy_recommender import get_strategy_recommendations
from data_visualizer import create_posting_schedule_chart, create_engagement_chart

st.set_page_config(page_title="Instagram Marketing Manager AI", layout="wide")

st.title("Instagram Marketing Manager AI")

st.image("assets/instagram_logo.svg", width=100)

st.sidebar.header("Input Instagram Profile")
username = st.sidebar.text_input("Enter Instagram username")
focus_area = st.sidebar.text_input("Enter your content focus area")

if username and focus_area:
    with st.spinner("Analyzing profile..."):
        profile_data = analyze_instagram_profile(username)
    
    if 'error' in profile_data:
        st.error(f"Error: {profile_data['error']}")
    elif profile_data:
        st.header("Profile Analysis")
        col1, col2, col3 = st.columns(3)
        col1.metric("Followers", profile_data['followers'])
        col2.metric("Following", profile_data['following'])
        col3.metric("Posts", profile_data['posts'])
        
        st.subheader("Top Hashtags")
        st.write(", ".join(profile_data['top_hashtags']))
        
        st.subheader("Engagement Rate")
        engagement_chart = create_engagement_chart(profile_data['engagement_rate'])
        st.plotly_chart(engagement_chart)
        
        st.header("Content Posting Plan")
        content_plan = generate_content_plan(profile_data, focus_area)
        st.table(pd.DataFrame(content_plan))
        
        st.subheader("Posting Schedule")
        schedule_chart = create_posting_schedule_chart(content_plan)
        st.plotly_chart(schedule_chart)
        
        st.header("Similar Accounts")
        st.write(", ".join(profile_data['similar_accounts']))
        
        st.header("Strategy Recommendations")
        recommendations = get_strategy_recommendations(profile_data, focus_area)
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")
    else:
        st.error("Unable to fetch profile data. Please check the username and try again.")
else:
    st.info("Please enter an Instagram username and content focus area to get started.")

st.sidebar.markdown("---")
st.sidebar.info("This app analyzes Instagram profiles and provides marketing recommendations. It does not store any personal data or require authentication.")
