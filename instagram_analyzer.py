import os
import logging
import nltk
from hikerapi import Client
from collections import Counter
from nltk.corpus import stopwords
from typing import Dict, List

nltk.download('stopwords', quiet=True)

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Get HikerAPI token from environment
HIKERAPI_TOKEN = os.getenv('HIKERAPI_TOKEN')

def analyze_instagram_profile(username: str) -> Dict:
    logger.info(f'Analyzing Instagram profile for username: {username}')
    
    try:
        # Initialize HikerAPI client
        client = Client(HIKERAPI_TOKEN)
        
        # Fetch user profile information
        logger.info("Fetching profile information")
        profile = client.user_by_username_v2(username)
        
        if 'user' not in profile:
            logger.error(f"Profile does not exist: {username}")
            return {'error': 'Profile does not exist'}
            
        user_info = profile['user']
        user_id = user_info['pk']
        
        # Fetch recent media
        logger.info("Fetching recent posts")
        media_response = client.user_medias_v1(user_id, amount=10)  # Get last 10 posts
        
        if 'items' not in media_response:
            posts = []
        else:
            posts = media_response['items']
        
        logger.info(f"Number of posts retrieved: {len(posts)}")
        
        hashtags = []
        likes = []
        comments = []
        
        # Analyze posts
        logger.info("Analyzing posts")
        for i, post in enumerate(posts):
            logger.info(f'Analyzing post {i+1}/{len(posts)}')
            try:
                # Extract hashtags from caption
                if post.get('caption') and post['caption'].get('text'):
                    caption_text = post['caption']['text']
                    # Extract hashtags from caption text
                    post_hashtags = [word[1:] for word in caption_text.split() if word.startswith('#')]
                    hashtags.extend(post_hashtags)
                
                # Get likes and comments count
                likes.append(post.get('like_count', 0))
                comments.append(post.get('comment_count', 0))
                
            except Exception as e:
                logger.error(f"Error processing post {i+1}: {str(e)}")
        
        # Calculate metrics
        logger.info("Calculating top hashtags")
        top_hashtags = [tag for tag, _ in Counter(hashtags).most_common(5)]
        
        logger.info("Calculating engagement metrics")
        followers_count = user_info.get('follower_count', 0)
        avg_likes = sum(likes) / len(likes) if likes else 0
        avg_comments = sum(comments) / len(comments) if comments else 0
        engagement_rate = (avg_likes + avg_comments) / followers_count * 100 if followers_count else 0
        
        # Get similar accounts (suggested users)
        logger.info("Fetching similar accounts")
        similar_accounts_response = client.user_related_profiles_gql(user_id)
        similar_accounts = []
        if 'users' in similar_accounts_response:
            similar_accounts = [user['username'] for user in similar_accounts_response['users'][:5]]
        
        logger.info("Analysis complete")
        return {
            'username': user_info['username'],
            'followers': followers_count,
            'following': user_info.get('following_count', 0),
            'posts': user_info.get('media_count', 0),
            'top_hashtags': top_hashtags,
            'engagement_rate': engagement_rate,
            'similar_accounts': similar_accounts
        }
        
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return {'error': f'An unexpected error occurred: {str(e)}'}

def extract_keywords(text: str) -> List[str]:
    stop_words = set(stopwords.words('english'))
    words = text.lower().split()
    return [word for word in words if word not in stop_words]
