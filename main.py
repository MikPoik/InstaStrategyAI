import streamlit as st
import pandas as pd
from io import StringIO
import logging
import os
from instagram_analyzer import analyze_instagram_profile
from content_generator import generate_content_plan
from strategy_recommender import get_strategy_recommendations
from data_visualizer import create_posting_schedule_chart, create_engagement_chart

# Retrieve Instagram credentials from environment variables
INSTAGRAM_USERNAME = os.environ.get('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.environ.get('INSTAGRAM_PASSWORD')

st.set_page_config(page_title="Instagram Marketing Manager AI", layout="wide")

st.title("Instagram Marketing Manager AI")

st.image("assets/instagram_logo.svg", width=100)

st.sidebar.header("Input Instagram Profile")
username = st.sidebar.text_input("Enter Instagram username to analyze")
focus_area = st.sidebar.text_input("Enter your content focus area")

if username and focus_area:
    # Set up StringIO object to capture log messages
    log_capture_string = StringIO()
    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logging.getLogger().addHandler(ch)

    with st.spinner("Analyzing profile..."):
        profile_data = analyze_instagram_profile(username)
    
    # Capture the log output
    log_contents = log_capture_string.getvalue()
    
    if 'error' in profile_data:
        st.error(f"Error: {profile_data['error']}")
        st.info("If you're experiencing rate limiting issues, please try again in a few minutes.")
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
        
        # Display logs in an expander
        with st.expander("View Analysis Logs"):
            st.text(log_contents)
    else:
        st.error("Unable to fetch profile data. Please check the username and try again.")
else:
    st.info("Please enter an Instagram username and content focus area to get started.")

st.sidebar.markdown("---")
st.sidebar.info("This app analyzes Instagram profiles and provides marketing recommendations. It does not store any personal data or require authentication. Instagram login credentials are securely managed through environment variables.")
