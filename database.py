import os
from flask_migrate import Migrate
from models import db
from datetime import datetime, timedelta
import json

migrate = Migrate()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        db.create_all()

def get_cached_profile(username):
    from flask import current_app
    from models import InstagramProfile
    
    if not current_app:
        raise RuntimeError("No Flask application context")
        
    profile = InstagramProfile.query.filter_by(username=username).first()
    
    if profile and profile.cache_valid_until and profile.cache_valid_until > datetime.utcnow():
        return profile.to_dict()
    return None

def cache_profile(profile_data):
    from flask import current_app
    from models import InstagramProfile, SimilarAccount
    
    if not current_app:
        raise RuntimeError("No Flask application context")
        
    profile = InstagramProfile.query.filter_by(username=profile_data['username']).first()
    if profile:
        # Update existing profile
        for key, value in profile_data.items():
            if key == 'top_hashtags':
                setattr(profile, key, json.dumps(value))
            elif key != 'similar_accounts' and hasattr(profile, key):
                setattr(profile, key, value)
        profile.last_updated = datetime.utcnow()
        profile.cache_valid_until = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    else:
        # Create new profile
        profile = InstagramProfile.from_api_response(profile_data)
        db.session.add(profile)
    
    # Clear existing similar accounts
    SimilarAccount.query.filter_by(profile_id=profile.id).delete()
    
    # Add new similar accounts
    for account_data in profile_data.get('similar_accounts', []):
        # Clean and encode post texts properly
        post_texts = account_data.get('post_texts', [])
        cleaned_post_texts = [text.strip() if isinstance(text, str) else str(text) for text in post_texts]
        
        similar_account = SimilarAccount(
            username=account_data['username'],
            full_name=account_data.get('full_name', ''),
            category=account_data.get('category', ''),
            followers=account_data.get('followers', 0),
            engagement_rate=account_data.get('engagement_rate', 0.0),
            top_hashtags=json.dumps(account_data.get('top_hashtags', [])),
            post_texts=json.dumps(cleaned_post_texts),
            profile=profile
        )
        db.session.add(similar_account)
    
    db.session.commit()
