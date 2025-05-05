from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from models.base import db
from config.constants import UserRoles

class User(UserMixin, db.Model):
    """User model for authentication and role management."""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('Role', secondary='user_roles', back_populates='users')
    
    # For Flask-Login
    def get_id(self):
        return str(self.user_id)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)
    
    @property
    def is_admin(self):
        return self.has_role(UserRoles.ADMIN)
    
    @property
    def is_principal(self):
        return self.has_role(UserRoles.PRINCIPAL)
    
    @property
    def is_hod(self):
        return self.has_role(UserRoles.HOD)
    
    @property
    def is_faculty(self):
        return self.has_role(UserRoles.FACULTY)
    
    @property
    def is_student(self):
        return self.has_role(UserRoles.STUDENT)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Role(db.Model):
    """Role model for RBAC."""
    __tablename__ = 'roles'
    
    role_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', secondary='user_roles', back_populates='roles')
    permissions = db.relationship('Permission', secondary='role_permissions', back_populates='roles')
    
    def __repr__(self):
        return f'<Role {self.name}>'


class UserRole(db.Model):
    """Association table between users and roles."""
    __tablename__ = 'user_roles'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), primary_key=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserRole {self.user_id}:{self.role_id}>'


class Permission(db.Model):
    """Permission model for granular access control."""
    __tablename__ = 'permissions'
    
    permission_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('Role', secondary='role_permissions', back_populates='permissions')
    
    def __repr__(self):
        return f'<Permission {self.name}>'


class RolePermission(db.Model):
    """Association table between roles and permissions."""
    __tablename__ = 'role_permissions'
    
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.permission_id'), primary_key=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RolePermission {self.role_id}:{self.permission_id}>'