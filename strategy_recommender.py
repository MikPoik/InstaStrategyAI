from typing import Dict, List
from chat_request import send_openai_request

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
    recommendations = eval(response)  # Convert JSON string to Python object
    return recommendations
