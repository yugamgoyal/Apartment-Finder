from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from models import db, User, generate_verification_token
from flask_session import Session
from flask_mail import Mail, Message
from config import ApplicationConfig
from datetime import datetime
from dotenv import load_dotenv
import os 
import re

load_dotenv()
app = Flask(__name__)
app.config.from_object(ApplicationConfig)
db.init_app(app)
server_session = Session(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

with app.app_context():
    db.create_all()

@app.route('/signup', methods=['POST'])
def signup_user():
    email = request.json['email']
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    password = request.json['password']
        
    user_present = User.query.filter_by(email=email).first()
    
    if user_present is not None:
        return jsonify({'error': "User already exists"}), 409
        
    if not re.search(r"@utexas\.edu$", email):
        return jsonify({'error': "Unathuorized - only utexas emails allowed"}), 401
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
    base_url = os.environ['BASE_URL']
    sender = os.environ['MAIL_USERNAME']
    link_for_verification = f"{base_url}/verify_account?verification_code={new_user.verify_token}"
    msg = Message("Hello from UT Austin Apartment Locator - EMAIL VERIFICATION NEEDED",
              sender = sender,
              recipients=[new_user.email],
              body=f"Hello from UT Austin Apartment Locator! We are happy you have chosen to join us.\n"
                   f"One last step before you can join our family. Please click the link below to verify your account. "
                   f"The link will expire in 24 hours.\n\n{link_for_verification}\n\nThank You,\nYugam & Nats")

    try:
        mail.send(msg)
    except Exception as e:
        return jsonify({'error': f'Failed to send verification email {e}'}), 500

    db.session.add(new_user)
    db.session.commit()
    
    # TODO: [AF-2] Should we keep this here, or should we just have sign-up as a non-cookie action
    # session['id'] = new_user.id
    
    return jsonify({
        'id': new_user.id,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "email": new_user.email
    })
    
@app.route('/login', methods=['POST'])
def login_user():
    email = request.json['email']
    password = request.json['password']
    
    user = User.query.filter_by(email=email).first()
    
    if user is None:
        return jsonify({'error': "Unauthorized: no account with this email"}), 401
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({'error': "Unauthorized: password incorrect"}), 401
    
    if not user.verified:
        return jsonify({'error': "Unauthorized: account not verified"}), 401

    session["id"] = user.id
    
    return jsonify({
        'id': user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email
    })
    
@app.route('/logout', methods=['POST'])
def logout_user():
    current_user_id = session.get('id')
    
    if current_user_id is None:
        return jsonify({'error': 'Unauthorized'}), 401
    
    session.pop("id", None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/@me', methods=['GET'])
def whoami():
    
    try:
        current_user_id = session.get('id')
    except Exception as e:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if current_user_id is None:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.filter_by(id=current_user_id).first()
    
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email
    })
    
@app.route('/verify_account', methods=['GET'])
def verify_account():
    token = request.args.get('verification_code')
    
    user = User.query.filter_by(verify_token=token).first()
    
    if not user:
        return jsonify({'error': 'Invalid Token'}), 400
    
    if datetime.now() < user.expiration_date:
        user.verified = True
        db.session.commit()
        session['id'] = user.id
        return jsonify({'message': 'Email verified successfully'}), 200
    else:
        user.verify_token = generate_verification_token(user.email)
        base_url = os.environ['BASE_URL']
        sender = os.environ['MAIL_USERNAME']
        link_for_verification = f"{base_url}/verify_account?verification_code={user.verify_token}"
        msg = Message("Hello from UT Austin Apartment Locator - EMAIL VERIFICATION NEEDED",
                sender=sender,
                recipients=[user.email],
                body=f"Hello from UT Austin Apartment Locator! We are happy you have chosen to join us.\n"
                    f"One last step before you can join our family. Please click the link below to verify your account. "
                    f"The link will expire in 24 hours.\n\n{link_for_verification}\n\nThank You,\nYugam & Nats")
        
        db.session.commit()
        
        try:
            mail.send(msg)
        except Exception as e:
            return jsonify({'error': 'Failed to send verification email'}), 500

        return jsonify({'error': 'Expired token'}), 400

if __name__ == '__main__':
    app.run(debug=True)