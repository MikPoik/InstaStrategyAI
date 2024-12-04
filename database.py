import os
from flask_migrate import Migrate
from models import db
from datetime import datetime

migrate = Migrate()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        db.create_all()

def get_cached_profile(username):
    from models import InstagramProfile
    profile = InstagramProfile.query.filter_by(username=username).first()
    
    if profile and profile.cache_valid_until and profile.cache_valid_until > datetime.utcnow():
        return profile.to_dict()
    return None

def cache_profile(profile_data):
    from models import InstagramProfile
    
    profile = InstagramProfile.query.filter_by(username=profile_data['username']).first()
    if profile:
        # Update existing profile
        for key, value in profile_data.items():
            if key in ['top_hashtags', 'similar_accounts']:
                setattr(profile, key, json.dumps(value))
            elif hasattr(profile, key):
                setattr(profile, key, value)
        profile.last_updated = datetime.utcnow()
        profile.cache_valid_until = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + \
                                  db.func.interval('1 day')
    else:
        # Create new profile
        profile = InstagramProfile.from_api_response(profile_data)
        db.session.add(profile)
    
    db.session.commit()
