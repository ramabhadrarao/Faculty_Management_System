import os
import secrets
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from models.user import User
from models.base import db


def hash_password(password):
    """Hash a password using pbkdf2_sha256."""
    return pbkdf2_sha256.hash(password)


def verify_password(password_hash, password):
    """Verify a password against a hash."""
    return pbkdf2_sha256.verify(password, password_hash)


def generate_token(length=32):
    """Generate a secure token for email verification, password reset, etc."""
    return secrets.token_urlsafe(length)


def create_user_tokens(user):
    """Create JWT access and refresh tokens for a user."""
    access_token = create_access_token(identity=user.user_id)
    refresh_token = create_refresh_token(identity=user.user_id)
    return access_token, refresh_token


def generate_password_reset_token(user):
    """Generate a password reset token and save it to the database."""
    token = generate_token()
    expiration = datetime.utcnow() + timedelta(hours=24)
    
    # Store token in the database
    user.reset_token = token
    user.reset_token_expiry = expiration
    db.session.commit()
    
    return token


def verify_reset_token(token):
    """Verify a password reset token and return the associated user."""
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or datetime.utcnow() > user.reset_token_expiry:
        return None
        
    return user