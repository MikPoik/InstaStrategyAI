import os
import logging
import nltk
from hikerapi import Client
from collections import Counter
from nltk.corpus import stopwords
from typing import Dict, List

from database import get_cached_profile, cache_profile
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

def get_medias(client, user_id, max_amount=None):
    medias = {}
    medias_len = -1
    end_cursor = None
    while len(medias) > medias_len:
        medias_len = len(medias)
        try:
            res = client.user_medias_chunk_v1(user_id=user_id, end_cursor=end_cursor)
            # Handle nested structure - res is a list of lists containing media items
            if res and isinstance(res, list) and len(res) > 0:
                for media_group in res:
                    if isinstance(media_group, list):
                        for item in media_group:
                            if isinstance(item, dict) and 'pk' in item:
                                medias[item['pk']] = item

                # Safely check for end_cursor
                if len(res) > 0 and isinstance(res[-1], list) and len(res[-1]) > 0:
                    last_item = res[-1][-1]
                    if isinstance(last_item, str):
                        end_cursor = last_item
                    else:
                        end_cursor = None
                else:
                    end_cursor = None
            else:
                break

            if not end_cursor:
                break

        except Exception as e:
            logger.error(f"Error occurred while fetching media: {e}")
            break

    return list(medias.values())
def analyze_instagram_profile(username: str, force_refresh: bool = False) -> Dict:
    logger.info(f'Analyzing Instagram profile for username: {username}')
    
    # Check cache first if not forcing refresh
    if not force_refresh:
        cached_data = get_cached_profile(username)
        if cached_data:
            logger.info(f'Retrieved cached data for {username}')
            return cached_data
    
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
        
        # Fetch recent posts
        logger.info("Fetching recent posts")
        posts = get_medias(client, user_id, max_amount=5)  # Limit to 50 posts
        logger.info(f"Number of posts retrieved: {len(posts)}")
        
        hashtags = []
        likes = []
        comments = []
        post_texts = []
        
        # Analyze posts
        logger.info("Analyzing posts")
        for i, post in enumerate(posts):
            logger.info(f'Analyzing post {i+1}/{len(posts)}')
            try:
                # Extract hashtags from caption
                if post.get('caption_text'):
                    caption_text = post['caption_text']
                    post_texts.append(caption_text.split("#")[0])
                    logger.info(f"Caption text: {caption_text}")
                    # Extract hashtags from caption text
                    post_hashtags = [word[1:] for word in caption_text.split() if word.startswith('#')]
                    hashtags.extend(post_hashtags)
                
                # Get likes and comments count
                likes.append(post.get('like_count', 0))
                logger.info(f"Likes for post {i+1}: {post.get('like_count', 0)}")
                comments.append(post.get('comment_count', 0))
                logger.info(f"Comments for post {i+1}: {post.get('comment_count'), 0}")
                
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
        try:
            similar_accounts_response = client.user_related_profiles_gql(user_id)
            similar_accounts = []
            # The response is a list of user objects, each containing username
            if isinstance(similar_accounts_response, list):
                similar_accounts = [
                    user['username'] 
                    for user in similar_accounts_response[:5] 
                    if isinstance(user, dict) and 'username' in user
                ]
            logger.info(f"Found {len(similar_accounts)} similar accounts")
        except Exception as e:
            logger.error(f"Error fetching similar accounts: {str(e)}")
            similar_accounts = []
        
        logger.info("Analysis complete")
        profile_data = {
            'username': user_info['username'],
            'followers': followers_count,
            'following': user_info.get('following_count', 0),
            'posts': user_info.get('media_count', 0),
            'top_hashtags': top_hashtags,
            'engagement_rate': engagement_rate,
            'similar_accounts': similar_accounts
        }
        
        # Cache the profile data
        cache_profile(profile_data)
        
        return profile_data
        
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return {'error': f'An unexpected error occurred: {str(e)}'}

def extract_keywords(text: str) -> List[str]:
    stop_words = set(stopwords.words('english'))
    words = text.lower().split()
    return [word for word in words if word not in stop_words]
