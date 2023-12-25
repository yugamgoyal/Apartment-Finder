import os
from flask_mail import Message
from dotenv import load_dotenv
from datetime import datetime, timedelta
from models import generate_verification_token

load_dotenv()

class UserUtil:
    def __init__(self, app, mail, db):
        self.app = app
        self.mail = mail
        self.db = db

    def create_send_verification(self, user):
        
        if datetime.now() > user.expiration_date:
            user.verify_token = generate_verification_token(user.email)
            user.expiration_date = datetime.utcnow() + timedelta(hours=24)
            self.db.session.commit()
        
        base_url = os.environ.get('BASE_URL')
        sender = os.environ.get('MAIL_USERNAME')

        if not base_url or not sender:
            raise ValueError("BASE_URL and MAIL_USERNAME must be set in the environment variables")

        link_for_verification = f"{base_url}/verify_account?verification_code={user.verify_token}"

        body = f"Hello from UT Austin Apartment Locator! We are happy you have chosen to join us.\n" \
               f"One last step before you can join our family. Please click the link below to verify your account. " \
               f"The link will expire in 24 hours.\n\n{link_for_verification}\n\nThank You,\nYugam, Nats, Sai"

        msg = Message("Hello from UT Austin Apartment Locator - EMAIL VERIFICATION NEEDED",
                      sender=sender,
                      recipients=[user.email],
                      body=body)

        self.db.session.commit()

        try:
            self.mail.send(msg)
            return {'message': 'Verification email sent successfully'}, 200
        except Exception as e:
            return {'error': f'Failed to send verification email. Error: {str(e)}'}, 500
    
    def verified(self, user):
        user.verified = True
        self.db.session.commit()
        
    def isVerified(self, user):
        return user.verified