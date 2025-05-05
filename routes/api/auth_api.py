from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from models.base import db
from models.user import User, Role
from config.constants import UserRoles
from utils.security import verify_password

auth_api_bp = Blueprint('auth_api', __name__)

@auth_api_bp.route('/login', methods=['POST'])
def login():
    """API endpoint for user login."""
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.verify_password(password):
        return jsonify({"error": "Invalid username or password"}), 401
    
    if not user.is_active:
        return jsonify({"error": "User is inactive"}), 401
    
    # Create tokens
    access_token = create_access_token(identity=user.user_id)
    refresh_token = create_refresh_token(identity=user.user_id)
    
    # Get user roles
    roles = [role.name for role in user.roles]
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.user_id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "roles": roles
        }
    }), 200

@auth_api_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({"access_token": access_token}), 200

@auth_api_bp.route('/register', methods=['POST'])
def register():
    """API endpoint for user registration."""
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    username = request.json.get('username', None)
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    first_name = request.json.get('first_name', None)
    last_name = request.json.get('last_name', None)
    
    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400
    
    # Create user
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=True
    )
    user.password = password  # This will be hashed
    
    # Add faculty role by default
    faculty_role = Role.query.filter_by(name=UserRoles.FACULTY).first()
    if faculty_role:
        user.roles.append(faculty_role)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "message": "User registered successfully",
        "user_id": user.user_id
    }), 201