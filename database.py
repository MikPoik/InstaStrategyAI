import os
from flask_migrate import Migrate
from models import db, PostText, SimilarAccountPostText
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

    profile = InstagramProfile.query.filter_by(username=username.lower()).first()

    if profile:
        print(f"Found profile for {username}")
        print(f"Cache valid until: {profile.cache_valid_until}")
        print(f"Current time: {datetime.utcnow()}")

        if profile.cache_valid_until and profile.cache_valid_until > datetime.utcnow():
            print(f"Using cached profile for {username}")
            return profile.to_dict()
        else:
            print("Cache expired")
    else:
        print(f"No profile found for {username}")
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
            elif key not in ['similar_accounts', 'post_texts'] and hasattr(profile, key):
                setattr(profile, key, value)

        # Clear existing post texts
        PostText.query.filter_by(profile_id=profile.id).delete()

        # Add new post texts
        for text in profile_data.get('post_texts', []):
            post_text = PostText(text_content=text, profile=profile)
            db.session.add(post_text)

        profile.last_updated = datetime.utcnow()
        profile.cache_valid_until = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    else:
        # Create new profile
        profile = InstagramProfile.from_api_response(profile_data)
        db.session.add(profile)
        db.session.flush()  # Flush to get the profile ID

        # Add post texts
        for text in profile_data.get('post_texts', []):
            post_text = PostText(text_content=text, profile=profile)
            db.session.add(post_text)

    # Clear existing similar accounts
    SimilarAccount.query.filter_by(profile_id=profile.id).delete()

    # Add new similar accounts
    for account_data in profile_data.get('similar_accounts', []):
        similar_account = SimilarAccount(
            username=account_data['username'],
            full_name=account_data.get('full_name', ''),
            category=account_data.get('category', ''),
            followers=account_data.get('followers', 0),
            engagement_rate=account_data.get('engagement_rate', 0.0),
            avg_likes=account_data.get('avg_likes', 0.0),
            avg_comments=account_data.get('avg_comments', 0.0),
            top_hashtags=json.dumps(account_data.get('top_hashtags', [])),
            profile=profile
        )
        db.session.add(similar_account)
        db.session.flush()  # Flush to get the similar account ID

        # Add post texts for similar account
        for text in account_data.get('post_texts', []):
            post_text = SimilarAccountPostText(
                text_content=text,
                similar_account=similar_account
            )
            db.session.add(post_text)

    db.session.commit()