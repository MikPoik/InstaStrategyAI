import random
from datetime import datetime, timedelta
from typing import Dict, List
from chat_request import send_openai_request

def generate_content_plan(profile_data: Dict, focus_area: str) -> List[Dict]:
    prompt = f"""
    Generate a content plan for an Instagram account with the following details:
    - Focus area: {focus_area}
    - Top hashtags: {', '.join(profile_data['top_hashtags'])}
    - Engagement rate: {profile_data['engagement_rate']:.2f}%

    Create a 7-day posting plan with the following structure:
    1. Day of the week
    2. Post type (Image, Carousel, Reel, IGTV)
    3. Caption theme
    4. Relevant hashtags (3-5)

    Provide the response in JSON format.
    """

    response = send_openai_request(prompt)
    content_plan = eval(response)  # Convert JSON string to Python object

    # Add posting times
    now = datetime.now()
    for i, post in enumerate(content_plan):
        post_time = now + timedelta(days=i)
        post_time = post_time.replace(hour=random.randint(9, 20), minute=random.randint(0, 59))
        post['posting_time'] = post_time.strftime("%Y-%m-%d %H:%M")

    return content_plan
