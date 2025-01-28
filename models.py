from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
db = SQLAlchemy()

def clean_json_string(json_str):
    if not json_str:
        return '[]'
    try:
        # Handle case where input is already a list
        if isinstance(json_str, list):
            return json.dumps(json_str)
        # Handle string input
        if isinstance(json_str, str):
            # Try to parse as JSON first
            try:
                parsed = json.loads(json_str)
                return json.dumps(parsed if isinstance(parsed, list) else [parsed])
            except json.JSONDecodeError:
                # If not valid JSON, treat as a single string
                return json.dumps([json_str])
        return '[]'
    except Exception as e:
        logger.error(f"Error cleaning JSON string: {e}")
        return '[]'

class SimilarAccount(db.Model):
    __tablename__ = 'similar_accounts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    category = db.Column(db.String(255))
    followers = db.Column(db.Integer)
    engagement_rate = db.Column(db.Float)
    top_hashtags = db.Column(db.Text)  # Stored as JSON
    post_texts = db.Column(db.Text)  # Stored as JSON array of post texts
    profile_id = db.Column(db.Integer, db.ForeignKey('instagram_profiles.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        try:
            return {
                'username': self.username,
                'full_name': self.full_name,
                'category': self.category,
                'followers': self.followers,
                'engagement_rate': self.engagement_rate,
                'top_hashtags': json.loads(self.top_hashtags) if self.top_hashtags else [],
                'post_texts': json.loads(clean_json_string(self.post_texts)) if self.post_texts else []
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for similar account {self.username}: {str(e)}")
            logger.error(f"JSON Data - top_hashtags: {self.top_hashtags}")
            logger.error(f"JSON Data - post_texts: {self.post_texts}")
            return {
                'username': self.username,
                'full_name': self.full_name,
                'category': self.category,
                'followers': self.followers,
                'engagement_rate': self.engagement_rate,
                'top_hashtags': [],
                'post_texts': []
            }

class InstagramProfile(db.Model):
    __tablename__ = 'instagram_profiles'
    similar_accounts_data = db.relationship('SimilarAccount', backref='profile', lazy=True)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    full_name = db.Column(db.String(255))
    biography = db.Column(db.Text)
    category = db.Column(db.String(255))
    followers = db.Column(db.Integer)
    following = db.Column(db.Integer)
    posts_count = db.Column(db.Integer)
    engagement_rate = db.Column(db.Float)
    top_hashtags = db.Column(db.Text)  # Stored as JSON
    similar_accounts = db.Column(db.Text)  # Stored as JSON
    post_texts = db.Column(db.Text)  # Stored as JSON array of post texts
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    cache_valid_until = db.Column(db.DateTime)

    def to_dict(self):
        try:
            # Get similar accounts from the relationship
            similar_accounts_list = [account.to_dict() for account in self.similar_accounts_data] if self.similar_accounts_data else []

            # Handle post_texts with clean_json_string
            try:
                post_texts = json.loads(clean_json_string(self.post_texts)) if self.post_texts else []
                logger.info(f"Successfully parsed post_texts for {self.username}: {len(post_texts)} posts")
            except Exception as e:
                logger.error(f"Error parsing post_texts for {self.username}: {str(e)}")
                logger.error(f"Raw post_texts: {self.post_texts[:100]}...")  # Log first 100 chars
                post_texts = []

            return {
                'username': self.username,
                'full_name': self.full_name,
                'biography': self.biography,
                'category': self.category,
                'followers': self.followers,
                'following': self.following,
                'posts': self.posts_count,
                'engagement_rate': self.engagement_rate,
                'top_hashtags': json.loads(self.top_hashtags) if self.top_hashtags else [],
                'similar_accounts': similar_accounts_list,
                'post_texts': post_texts
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for profile {self.username}: {str(e)}")
            logger.error(f"JSON Data - top_hashtags: {self.top_hashtags}")
            logger.error(f"JSON Data - similar_accounts: {self.similar_accounts}")
            logger.error(f"JSON Data - post_texts: {self.post_texts}")
            return {
                'username': self.username,
                'full_name': self.full_name,
                'biography': self.biography,
                'category': self.category,
                'followers': self.followers,
                'following': self.following,
                'posts': self.posts_count,
                'engagement_rate': self.engagement_rate,
                'top_hashtags': [],
                'similar_accounts': [],
                'post_texts': []
            }

    @staticmethod
    def from_api_response(data):
        return InstagramProfile(
            username=data['username'],
            full_name=data.get('full_name', ''),
            biography=data.get('biography', ''),
            category=data.get('category', ''),
            followers=data['followers'],
            following=data['following'],
            posts_count=data['posts'],
            engagement_rate=data['engagement_rate'],
            top_hashtags=json.dumps(data['top_hashtags']),
            similar_accounts=json.dumps(data['similar_accounts']),
            post_texts=clean_json_string(data.get('post_texts', [])),
            cache_valid_until=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + 
                            timedelta(days=1)
        )