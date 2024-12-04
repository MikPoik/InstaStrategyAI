from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    subscription_status = db.Column(db.String(20), default='free')
    subscription_end = db.Column(db.DateTime)
    stripe_customer_id = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InstagramProfile(db.Model):
    __tablename__ = 'instagram_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    followers = db.Column(db.Integer)
    following = db.Column(db.Integer)
    posts_count = db.Column(db.Integer)
    engagement_rate = db.Column(db.Float)
    top_hashtags = db.Column(db.Text)  # Stored as JSON
    similar_accounts = db.Column(db.Text)  # Stored as JSON
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    cache_valid_until = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'username': self.username,
            'followers': self.followers,
            'following': self.following,
            'posts': self.posts_count,
            'engagement_rate': self.engagement_rate,
            'top_hashtags': json.loads(self.top_hashtags),
            'similar_accounts': json.loads(self.similar_accounts)
        }

    @staticmethod
    def from_api_response(data):
        return InstagramProfile(
            username=data['username'],
            followers=data['followers'],
            following=data['following'],
            posts_count=data['posts'],
            engagement_rate=data['engagement_rate'],
            top_hashtags=json.dumps(data['top_hashtags']),
            similar_accounts=json.dumps(data['similar_accounts']),
            cache_valid_until=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + 
                            timedelta(days=1)
        )
