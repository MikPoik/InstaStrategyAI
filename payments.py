import os
import stripe
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import db, User

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]

payments = Blueprint("payments", __name__)

# Define subscription plans
SUBSCRIPTION_PLANS = {
    'basic': {
        'name': 'Basic Plan',
        'price_id': 'price_H1234567890',  # Replace with actual Stripe price ID
        'features': ['Profile Analysis', 'Basic Reports']
    },
    'pro': {
        'name': 'Pro Plan',
        'price_id': 'price_P1234567890',  # Replace with actual Stripe price ID
        'features': ['Advanced Analytics', 'Content Planning', 'Priority Support']
    }
}

@payments.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    plan = request.json.get('plan')
    if plan not in SUBSCRIPTION_PLANS:
        return jsonify({'error': 'Invalid plan selected'}), 400

    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            line_items=[{
                'price': SUBSCRIPTION_PLANS[plan]['price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'payment/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'pricing',
        )
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@payments.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET', '')
        )
    except ValueError as e:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': 'Invalid signature'}), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_update(subscription)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_cancelled(subscription)

    return jsonify({'status': 'success'})

def handle_checkout_session(session):
    customer_email = session.get('customer_email')
    user = User.query.filter_by(email=customer_email).first()
    if user:
        user.stripe_customer_id = session.get('customer')
        user.subscription_status = 'active'
        user.subscription_end = datetime.utcnow() + timedelta(days=30)
        db.session.commit()

def handle_subscription_update(subscription):
    user = User.query.filter_by(stripe_customer_id=subscription.get('customer')).first()
    if user:
        user.subscription_status = subscription.get('status', 'active')
        if subscription.get('current_period_end'):
            user.subscription_end = datetime.fromtimestamp(subscription['current_period_end'])
        db.session.commit()

def handle_subscription_cancelled(subscription):
    user = User.query.filter_by(stripe_customer_id=subscription.get('customer')).first()
    if user:
        user.subscription_status = 'cancelled'
        user.subscription_end = datetime.utcnow()
        db.session.commit()
