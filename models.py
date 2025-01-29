import json
import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

db = SQLAlchemy()

class PostText(db.Model):
    __tablename__ = 'post_texts'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('instagram_profiles.id'))
    text_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'text_content': self.text_content,
            'created_at': self.created_at.isoformat()
        }

class SimilarAccountPostText(db.Model):
    __tablename__ = 'similar_account_post_texts'

    id = db.Column(db.Integer, primary_key=True)
    similar_account_id = db.Column(db.Integer, db.ForeignKey('similar_accounts.id'))
    text_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'text_content': self.text_content,
            'created_at': self.created_at.isoformat()
        }

class SimilarAccount(db.Model):
    __tablename__ = 'similar_accounts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    category = db.Column(db.String(255))
    followers = db.Column(db.Integer)
    engagement_rate = db.Column(db.Float)
    avg_likes = db.Column(db.Float)
    avg_comments = db.Column(db.Float)
    top_hashtags = db.Column(db.Text)  # Stored as JSON
    profile_id = db.Column(db.Integer, db.ForeignKey('instagram_profiles.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_texts = db.relationship('SimilarAccountPostText', backref='similar_account', lazy=True)

    def to_dict(self):
        try:
            return {
                'username': self.username,
                'full_name': self.full_name,
                'category': self.category,
                'followers': self.followers,
                'engagement_rate': self.engagement_rate,
                'avg_likes': self.avg_likes,
                'avg_comments': self.avg_comments,
                'top_hashtags': json.loads(self.top_hashtags) if self.top_hashtags else [],
                'post_texts': [post.text_content for post in self.post_texts]
            }
        except Exception as e:
            logger.error(f"Error in similar account {self.username}: {str(e)}")
            return {
                'username': self.username,
                'full_name': self.full_name,
                'category': self.category,
                'followers': self.followers,
                'engagement_rate': self.engagement_rate,
                'avg_likes': 0,
                'avg_comments': 0,
                'top_hashtags': [],
                'post_texts': []
            }

class InstagramProfile(db.Model):
    __tablename__ = 'instagram_profiles'
    similar_accounts_data = db.relationship('SimilarAccount', backref='profile', lazy=True)
    post_texts = db.relationship('PostText', backref='profile', lazy=True)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    full_name = db.Column(db.String(255))
    biography = db.Column(db.Text)
    category = db.Column(db.String(255))
    followers = db.Column(db.Integer)
    following = db.Column(db.Integer)
    posts_count = db.Column(db.Integer)
    engagement_rate = db.Column(db.Float)
    avg_likes = db.Column(db.Float)
    avg_comments = db.Column(db.Float)
    top_hashtags = db.Column(db.Text)  # Stored as JSON
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    cache_valid_until = db.Column(db.DateTime)

    def to_dict(self):
        try:
            similar_accounts_list = [account.to_dict() for account in self.similar_accounts_data] if self.similar_accounts_data else []

            return {
                'username': self.username,
                'full_name': self.full_name,
                'biography': self.biography,
                'category': self.category,
                'followers': self.followers,
                'following': self.following,
                'posts': self.posts_count,
                'engagement_rate': self.engagement_rate,
                'avg_likes': self.avg_likes,
                'avg_comments': self.avg_comments,
                'top_hashtags': json.loads(self.top_hashtags) if self.top_hashtags else [],
                'similar_accounts': similar_accounts_list,
                'post_texts': [post.text_content for post in self.post_texts]
            }
        except Exception as e:
            logger.error(f"Error in profile {self.username}: {str(e)}")
            return {
                'username': self.username,
                'full_name': self.full_name,
                'biography': self.biography,
                'category': self.category,
                'followers': self.followers,
                'following': self.following,
                'posts': self.posts_count,
                'engagement_rate': self.engagement_rate,
                'avg_likes': 0,
                'avg_comments': 0,
                'top_hashtags': [],
                'similar_accounts': [],
                'post_texts': []
            }

    @staticmethod
    def from_api_response(data):
        profile = InstagramProfile(
            username=data['username'],
            full_name=data.get('full_name', ''),
            biography=data.get('biography', ''),
            category=data.get('category', ''),
            followers=data['followers'],
            following=data['following'],
            posts_count=data['posts'],
            engagement_rate=data['engagement_rate'],
            avg_likes=data.get('avg_likes', 0),
            avg_comments=data.get('avg_comments', 0),
            top_hashtags=json.dumps(data['top_hashtags']),
            cache_valid_until=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        )
        return profile

def clean_json_string(json_str):
    """
    Clean and normalize JSON string for reading from database
    """
    if not json_str:
        return '[]'
    try:
        # Handle string input
        if isinstance(json_str, str):
            try:
                # Parse as JSON
                parsed = json.loads(json_str)
                if isinstance(parsed, list):
                    return json.dumps(parsed)
                return json.dumps([parsed])
            except json.JSONDecodeError:
                # If not valid JSON, treat as single string
                return json.dumps([json_str])
        # Handle list input
        elif isinstance(json_str, list):
            return json.dumps(json_str)
        return '[]'
    except Exception as e:
        logger.error(f"Error cleaning JSON string: {e}")
        return '[]'