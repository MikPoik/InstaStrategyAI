import os
import json
import requests
from flask import Blueprint, redirect, request, url_for, flash, render_template
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient
from models import db, User

GOOGLE_CLIENT_ID = os.environ["GOOGLE_OAUTH_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_OAUTH_CLIENT_SECRET"]
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
STRIPE_PUBLISHABLE_KEY = os.environ["STRIPE_PUBLISHABLE_KEY"]

auth = Blueprint("auth", __name__)
client = WebApplicationClient(GOOGLE_CLIENT_ID)
replit_domain = f"https://10d60081-f259-42b7-8ea6-11d107cc22e5-00-5nk7acteyu8c.picard.replit.dev"

def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

@auth.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect('/')
        
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    print(replit_domain)
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=f"{replit_domain}/auth/login/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth.route("/login/callback")
def callback():
    print("login callback")
    # Debug logging
    print(f"Request URL: {request.url}")
    print(f"Request args: {request.args}")
    print(f"Request headers: {dict(request.headers)}")
    print(f"Request path: {request.path}")
    
    code = request.args.get("code")
    if not code:
        print("No code received in callback")
        return "Authentication failed - no code received", 400
        
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    callback_url = request.base_url
    print(f"Callback URL: {callback_url}")
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=callback_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))
    
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    if userinfo_response.json().get("email_verified"):
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json().get("given_name", users_email.split('@')[0])
    else:
        return "User email not verified by Google.", 400

    user = User.query.filter_by(email=users_email).first()
    if not user:
        user = User(username=users_name, email=users_email)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect('/')

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))

@auth.route("/pricing")
def pricing():
    return render_template(
        'pricing.html',
        stripe_public_key=STRIPE_PUBLISHABLE_KEY
    )
