from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

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
                'post_texts': json.loads(self.post_texts) if self.post_texts else []
            }
        except json.JSONDecodeError:
            logger.error(f"JSON decode error for similar account {self.username}")
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
                'similar_accounts': json.loads(self.similar_accounts) if self.similar_accounts else [],
                'post_texts': json.loads(self.post_texts) if self.post_texts else []
            }
        except json.JSONDecodeError:
            logger.error(f"JSON decode error for profile {self.username}")
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
            post_texts=json.dumps(data.get('post_texts', [])),
            cache_valid_until=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + 
                            timedelta(days=1)
        )
