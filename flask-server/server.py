from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from models import db, User, generate_verification_token
from flask_session import Session
from flask_mail import Mail
from config import ApplicationConfig
from datetime import datetime
from dotenv import load_dotenv
import re

from common.user_util import UserUtil

load_dotenv()
app = Flask(__name__)
app.config.from_object(ApplicationConfig)
db.init_app(app)
server_session = Session(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

user_util = UserUtil(app, mail, db)

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
    
    user_util.create_send_verification(new_user)        

    db.session.add(new_user)
    db.session.commit()
    
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
        user_util.create_send_verification(user)        
        
        db.session.commit()

        return jsonify({'error': 'Expired token'}), 400

if __name__ == '__main__':
    app.run(debug=True)