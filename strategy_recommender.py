import logging
from typing import Dict, List
from chat_request import send_openai_request
import json

logger = logging.getLogger(__name__)

def get_strategy_recommendations(profile_data: Dict, focus_area: str) -> List[str]:
    prompt = f"""
    Provide strategic recommendations for an Instagram account with the following details:
    - Username: {profile_data['username']}
    - Full Name: {profile_data['full_name']}
    - Biography: {profile_data['biography']}
    - Category: {profile_data['category']}
    - Followers: {profile_data['followers']}
    - Posts: {profile_data['posts']}
    - Average likes per post: {profile_data['avg_likes']}
    - Average comments per post: {profile_data['avg_comments']}
    - Engagement rate: {profile_data['engagement_rate']:.2f}%
    - Top hashtags: {', '.join(profile_data['top_hashtags'])}
    - Focus area: {focus_area}

    Generate 5 specific, actionable recommendations to improve the account's performance and reach.
    Provide the response as a JSON array of strings.
    """
    print(prompt)
    response = send_openai_request(prompt)
    print(response)
    try:
        recommendations = json.loads(response)
        if isinstance(recommendations, list):
            recommendations = [str(rec) for rec in recommendations if rec]
        elif isinstance(recommendations, dict):
            recommendations = [str(value) for value in recommendations.values() if value]
        else:
            raise ValueError('Unexpected recommendations format')
        
        if not recommendations:
            raise ValueError('No valid recommendations found')

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f'Error processing recommendations: {e}')
        logger.error(f'Received response: {response}')
        recommendations = [
            'Increase posting frequency to boost engagement',
            'Use trending hashtags related to your niche',
            'Collaborate with influencers in your industry',
            'Create more video content, especially Reels',
            'Engage with your followers by responding to comments and messages'
        ]

    return recommendations[:5]  # Ensure we always return exactly 5 recommendations
