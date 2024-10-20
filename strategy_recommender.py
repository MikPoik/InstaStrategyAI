import logging
from typing import Dict, List
from chat_request import send_openai_request
import json

logger = logging.getLogger(__name__)

def get_strategy_recommendations(profile_data: Dict, focus_area: str) -> List[str]:
    prompt = f"""
    Provide strategic recommendations for an Instagram account with the following details:
    - Username: {profile_data['username']}
    - Followers: {profile_data['followers']}
    - Posts: {profile_data['posts']}
    - Engagement rate: {profile_data['engagement_rate']:.2f}%
    - Top hashtags: {', '.join(profile_data['top_hashtags'])}
    - Focus area: {focus_area}

    Generate 5 specific, actionable recommendations to improve the account's performance and reach.
    Provide the response as a JSON array of strings.
    """

    response = send_openai_request(prompt)
    
    try:
        recommendations = json.loads(response)
        if not isinstance(recommendations, list):
            raise ValueError('Unexpected recommendations format')
    except json.JSONDecodeError as e:
        logger.error(f'Error decoding JSON: {e}')
        logger.error(f'Received response: {response}')
        recommendations = ['Error: Unable to generate recommendations. Please try again.']
    except ValueError as e:
        logger.error(f'Error processing recommendations: {e}')
        recommendations = ['Error: Unexpected recommendations format. Please try again.']
    
    return recommendations
