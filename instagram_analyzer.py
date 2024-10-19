import instaloader
import nltk
from collections import Counter
from nltk.corpus import stopwords
from typing import Dict, List

nltk.download('stopwords', quiet=True)

def analyze_instagram_profile(username: str) -> Dict:
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except instaloader.exceptions.ProfileNotExistsException:
        return None

    posts = list(profile.get_posts())[:50]  # Analyze last 50 posts
    
    hashtags = []
    likes = []
    comments = []
    
    for post in posts:
        hashtags.extend(post.caption_hashtags)
        likes.append(post.likes)
        comments.append(post.comments)
    
    top_hashtags = [tag for tag, _ in Counter(hashtags).most_common(5)]
    
    avg_likes = sum(likes) / len(likes) if likes else 0
    avg_comments = sum(comments) / len(comments) if comments else 0
    engagement_rate = (avg_likes + avg_comments) / profile.followers * 100 if profile.followers else 0
    
    similar_accounts = [account.username for account in profile.get_similar_accounts()][:5]
    
    return {
        'username': profile.username,
        'followers': profile.followers,
        'following': profile.followees,
        'posts': profile.mediacount,
        'top_hashtags': top_hashtags,
        'engagement_rate': engagement_rate,
        'similar_accounts': similar_accounts
    }

def extract_keywords(text: str) -> List[str]:
    stop_words = set(stopwords.words('english'))
    words = text.lower().split()
    return [word for word in words if word not in stop_words]
