import instaloader
import nltk
import logging
import os
from collections import Counter
from nltk.corpus import stopwords
from typing import Dict, List
from instaloader import RateController
from instaloader.exceptions import ConnectionException, BadCredentialsException

nltk.download('stopwords', quiet=True)

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Retrieve Instagram credentials from environment variables
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

class LoggingRateController(RateController):
    def sleep(self, secs):
        logger.info(f"Rate limit reached. Waiting for {secs:.2f} seconds.")
        super().sleep(secs)

def analyze_instagram_profile(username: str) -> Dict:
    
    L = instaloader.Instaloader(
        rate_controller=lambda context: LoggingRateController(context),
        sleep=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_comments=True,
        iphone_support=False
    )
    logger.info(f'Analyzing Instagram profile for username: {username}')

    if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
        try:
            logger.info("Attempting to log in with provided credentials")
            L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            logger.info("Login successful")
        except BadCredentialsException as e:
            logger.error(f"Login failed: Invalid credentials {str(e)}")
            return {'error': 'Login failed: Invalid credentials'}
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return {'error': f'Login failed: {str(e)}'}
    else:
        logger.info("Login credentials not set!")

    try:
        logger.info("Fetching profile information")
        profile = instaloader.Profile.from_username(L.context, username)
        logger.info(f"Profile fetched: {profile.username}")
        logger.info("Fetching recent posts")
        posts = list(profile.get_posts())[:10]  # Analyze last 10 posts
        logger.info(f"Number of posts retrieved: {len(posts)}")

        hashtags = []
        likes = []
        comments = []

        logger.info("Analyzing posts")
        for i, post in enumerate(posts):
            logger.info(f'Analyzing post {i+1}/{len(posts)}')
            try:
                hashtags.extend(post.caption_hashtags)
                likes.append(post.likes)
                comments.append(post.comments)
            except AttributeError as e:
                logger.error(f"Error processing post {i+1}: {str(e)}")

        logger.info("Calculating top hashtags")
        top_hashtags = [tag for tag, _ in Counter(hashtags).most_common(5)]

        logger.info("Calculating engagement metrics")
        avg_likes = sum(likes) / len(likes) if likes else 0
        avg_comments = sum(comments) / len(comments) if comments else 0
        engagement_rate = (avg_likes + avg_comments) / profile.followers * 100 if profile.followers else 0

        logger.info("Fetching similar accounts")
        similar_accounts = [account.username for account in profile.get_similar_accounts()][:5]

        logger.info("Analysis complete")
        return {
            'username': profile.username,
            'followers': profile.followers,
            'following': profile.followees,
            'posts': profile.mediacount,
            'top_hashtags': top_hashtags,
            'engagement_rate': engagement_rate,
            'similar_accounts': similar_accounts
        }
    except instaloader.exceptions.ProfileNotExistsException:
        logger.error(f"Profile does not exist: {username}")
        return {'error': 'Profile does not exist'}
    except ConnectionException as e:
        logger.error(f'Connection error: {str(e)}')
        return {'error': 'Connection error. Please try again later.'}
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return {'error': f'An unexpected error occurred: {str(e)}'}

def extract_keywords(text: str) -> List[str]:
    stop_words = set(stopwords.words('english'))
    words = text.lower().split()
    return [word for word in words if word not in stop_words]