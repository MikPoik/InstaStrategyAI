import random
from datetime import datetime, timedelta
from typing import Dict, List
from chat_request import send_openai_request
import json
import logging

logger = logging.getLogger(__name__)

def generate_content_plan(profile_data: Dict, focus_area: str) -> List[Dict]:
    prompt = f"""
    Generate a content plan for an Instagram account with the following details:
    - Focus area: {focus_area}
    - Top hashtags: {', '.join(profile_data['top_hashtags'])}
    - Engagement rate: {profile_data['engagement_rate']:.2f}%

    Create a 7-day posting plan with the following structure:
    1. Day of the week (e.g., Monday, Tuesday, etc.)
    2. Post type (Image, Carousel, Reel, IGTV)
    3. Caption theme
    4. Relevant hashtags (3-5)

    Provide the response in JSON format, with each post as a dictionary containing 'day', 'post_type', 'caption_theme', and 'hashtags' keys.
    """

    response = send_openai_request(prompt)

    try:
        content_plan = json.loads(response)
        
        if not isinstance(content_plan, list):
            raise ValueError('Content plan should be a list of dictionaries')
        
        formatted_content_plan = []
        for post in content_plan:
            if not isinstance(post, dict):
                logger.warning(f"Unexpected post format: {post}")
                continue
            
            formatted_post = {
                'day': post.get('day', ''),
                'post_type': post.get('post_type', ''),
                'caption_theme': post.get('caption_theme', ''),
                'hashtags': post.get('hashtags', [])
            }
            
            if all(formatted_post.values()):
                formatted_content_plan.append(formatted_post)
            else:
                logger.warning(f"Skipping incomplete post: {post}")
        
        if not formatted_content_plan:
            raise ValueError('No valid posts in the content plan')
        
    except json.JSONDecodeError as e:
        logger.error(f'Error decoding JSON: {e}')
        logger.error(f'Received response: {response}')
        raise ValueError('Invalid JSON response from OpenAI API')
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        raise ValueError(f'Error processing content plan: {str(e)}')

    # Add posting times
    now = datetime.now()
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for i, post in enumerate(formatted_content_plan):
        post_time = now + timedelta(days=i)
        post_time = post_time.replace(hour=random.randint(9, 20), minute=random.randint(0, 59))
        post['posting_time'] = post_time.strftime("%Y-%m-%d %H:%M")
        if not post['day']:
            post['day'] = days_of_week[post_time.weekday()]

    return formatted_content_plan
