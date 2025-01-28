import random
from datetime import datetime, timedelta
from typing import Dict, List
from chat_request import send_openai_request
import json
import logging

logger = logging.getLogger(__name__)

def get_formatted_post_texts(post_texts):
    if not post_texts:
        return []

    try:
        # If it's already a list, return it
        if isinstance(post_texts, list):
            return post_texts

        # If it's a string, try to parse it
        if isinstance(post_texts, str):
            # Try standard JSON parsing first
            try:
                return json.loads(post_texts)
            except json.JSONDecodeError:
                # Handle malformed JSON like {"text1","text2"}
                print("Failed to load Post Text Json")
                #if post_texts.startswith('{') and post_texts.endswith('}'):
                    # Remove braces and split by comma
                #    texts = post_texts[1:-1].split('","')
                    # Clean up quotes and whitespace
                #    return [text.strip('" ') for text in texts if text.strip()]

        return []
    except Exception as e:
        logger.error(f'Error formatting post texts: {str(e)}')
        return []

        
def generate_content_plan(profile_data: Dict, focus_area: str) -> List[Dict]:
    post_texts = get_formatted_post_texts(profile_data.get('post_texts', []))
    print(post_texts)
    prompt = f"""
    # Generate a content plan for an Instagram account with the following details:
    - Username: {profile_data['username']}
    - Full Name: {profile_data['full_name']}
    - Category: {profile_data['category']}
    - Followers: {profile_data['followers']}
    - Focus area: {focus_area}
    - Top hashtags: {', '.join(profile_data['top_hashtags'])}
    - Engagement rate: {profile_data['engagement_rate']:.2f}%
    - Recent post sample texts:
    > {profile_data['post_texts'][0].split('","')[0].replace('{"',"")}
    > {profile_data['post_texts'][1].split('","')[0].replace('{"',"")}

    

    ## Create a 7-day posting plan with the following structure:
    1. Day of the week (e.g., Monday, Tuesday, etc.)
    2. Post type (Image, Carousel, Reel)
    3. Caption theme and Title
    4. Caption text content
    4. Relevant hashtags (3-5)

    Use clear and direct language, avoid complex terminology. Aim for a Flesch reading score of 80 or higher. Use active language. Avoid adverbs. Avoid buzzwords and instead use simple language. Use professional jargon when necessary. Avoid a salesy or overly enthusiastic tone and instead convey calm confidence.

    Write an engaging Instagram post on each topic. Analyze my writing style from examples and simulate it. Use a structure that is 50% creative and 50% persuasive, and emphasize important points in a Spartan manner.
Important!! Remember to use low complexity and make the text human-like.

    Kirjoita Postauksien sisältö ja otsikko _SUOMEKSI_

    Provide the response in JSON format, with each post as a dictionary containing 'day', 'post_type', 'caption_theme','caption_text' and 'hashtags' keys.
    """
    print(prompt)
    response = send_openai_request(prompt)
    print(response)

    try:
        content_plan = json.loads(response)
        print(content_plan)
        if isinstance(content_plan, dict) and 'posts' in content_plan:
            content_plan = content_plan['posts']
        if isinstance(content_plan, dict):
            content_plan = [content_plan]
        elif not isinstance(content_plan, list):
            raise ValueError('Unexpected content plan format')
        
        formatted_content_plan = []
        for post in content_plan:
            if not isinstance(post, dict):
                logger.warning(f'Skipping invalid post: {post}')
                continue
            
            formatted_post = {
                'day': post.get('day', ''),
                'post_type': post.get('post_type', ''),
                'caption_theme': post.get('caption_theme', ''),
                'caption_text': post.get('caption_text', ''),
                'hashtags': post.get('hashtags', [])
            }
            
            if all(formatted_post.values()):
                formatted_content_plan.append(formatted_post)
        
        if not formatted_content_plan:
            raise ValueError('No valid posts in the content plan')

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f'Error processing content plan: {str(e)}')
        logger.error(f'Received response: {response}')
        print("Default plan")
        # Create a default content plan
        formatted_content_plan = [
            {
                'day': 'Monday',
                'post_type': 'Image',
                'caption_theme': 'Motivational Monday',
                'hashtags': ['#MondayMotivation', '#NewWeek', '#GoalSetting']
            },
            {
                'day': 'Wednesday',
                'post_type': 'Carousel',
                'caption_theme': 'Tips and Tricks',
                'hashtags': ['#WednesdayWisdom', '#TipsAndTricks', '#LearnSomethingNew']
            },
            {
                'day': 'Friday',
                'post_type': 'Reel',
                'caption_theme': 'Fun Friday',
                'hashtags': ['#FridayFun', '#WeekendVibes', '#HappyFriday']
            },
            {
                'day': 'Sunday',
                'post_type': 'IGTV',
                'caption_theme': 'Weekly Recap',
                'hashtags': ['#SundayThoughts', '#WeeklyRecap', '#NewWeekNewGoals']
            }
        ]

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
