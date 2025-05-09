import sys
import os
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from flask_migrate import Migrate  # Added Flask-Migrate
from datetime import datetime

# Import database
from models.base import db
from models.user import User, Role, UserRole, Permission
from models.faculty import Faculty
from models.department import College, Department, Program, Branch
from config.config import config

# Import blueprints
from routes.auth_routes import auth_bp
from routes.faculty_routes import faculty_bp
from routes.hod_routes import hod_bp
from routes.admin_routes import admin_bp
from routes.api.auth_api import auth_api_bp
from routes.api.faculty_api import faculty_api_bp
from routes.api.admin_api import admin_api_bp

# Initialize extensions
login_manager = LoginManager()
jwt = JWTManager()
mail = Mail()
csrf = CSRFProtect()
migrate = Migrate()  # Initialize Flask-Migrate

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate with app and db
    login_manager.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    
    # Enable CORS for API routes only
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Setup middleware
    from middleware.rbac_middleware import setup_rbac
    setup_rbac(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(faculty_bp, url_prefix='/faculty')
    app.register_blueprint(hod_bp, url_prefix='/hod')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Register API blueprints
    app.register_blueprint(auth_api_bp, url_prefix='/api/auth')
    app.register_blueprint(faculty_api_bp, url_prefix='/api/faculty')
    app.register_blueprint(admin_api_bp, url_prefix='/api/admin')
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Custom error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
        
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    # Exempting API routes from CSRF protection
    @app.before_request
    def csrf_protect():
        if request.path.startswith('/api/'):
            return None
        return csrf.protect()
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    # Root route
    # Root route
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin or current_user.is_principal:
                return redirect(url_for('admin.dashboard'))
            elif current_user.is_hod:
                return redirect(url_for('hod.dashboard'))
            else:
                return redirect(url_for('faculty.dashboard'))
        return render_template('index.html', now=datetime.now())
    
    # Initialize database tables - Using Flask-Migrate instead of db.create_all()
    # Flask-Migrate will handle table creation through migrations
    with app.app_context():
        # Only create initial roles, db.create_all() is no longer needed
        _create_initial_roles()
        _create_lookup_tables()  # Add this line
    
    return app


def _create_initial_roles():
    """Create initial roles if they don't exist."""
    from config.constants import UserRoles
    
    # Check if roles already exist
    if Role.query.first() is not None:
        return
    
    # Create roles
    roles = [
        {'name': UserRoles.ADMIN, 'description': 'Administrator with full access'},
        {'name': UserRoles.PRINCIPAL, 'description': 'College principal'},
        {'name': UserRoles.HOD, 'description': 'Head of Department'},
        {'name': UserRoles.FACULTY, 'description': 'Faculty member'},
        {'name': UserRoles.STUDENT, 'description': 'Student'}
    ]
    
    for role_data in roles:
        role = Role(name=role_data['name'], description=role_data['description'])
        db.session.add(role)
    
    # Create default admin user if no users exist
    if User.query.first() is None:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            is_active=True
        )
        admin_user.password = 'admin123'  # This will be hashed
        db.session.add(admin_user)
        db.session.commit()
        
        # Assign admin role
        admin_role = Role.query.filter_by(name=UserRoles.ADMIN).first()
        admin_user.roles.append(admin_role)
    
    db.session.commit()

def _create_lookup_tables():
    """Create the initial lookup table values if they don't exist."""
    from models.faculty import LookupTable
    from config.constants import PUBLICATION_TYPES, WORKSHOP_TYPES, FDP_MDP_TYPES, AWARD_CATEGORIES
    
    # Create publication types
    for value in PUBLICATION_TYPES:
        if not LookupTable.query.filter_by(lookup_type='publication_type', lookup_value=value).first():
            lookup = LookupTable(lookup_type='publication_type', lookup_value=value)
            db.session.add(lookup)
    
    # Create workshop types
    for value in WORKSHOP_TYPES:
        if not LookupTable.query.filter_by(lookup_type='workshop_type', lookup_value=value).first():
            lookup = LookupTable(lookup_type='workshop_type', lookup_value=value)
            db.session.add(lookup)
    
    # Create FDP/MDP types
    for value in FDP_MDP_TYPES:
        if not LookupTable.query.filter_by(lookup_type='fdp_mdp_type', lookup_value=value).first():
            lookup = LookupTable(lookup_type='fdp_mdp_type', lookup_value=value)
            db.session.add(lookup)
    
    # Create award categories
    for value in AWARD_CATEGORIES:
        if not LookupTable.query.filter_by(lookup_type='award_category', lookup_value=value).first():
            lookup = LookupTable(lookup_type='award_category', lookup_value=value)
            db.session.add(lookup)
    
    # Create some common funding agencies
    funding_agencies = [
        'UGC', 'AICTE', 'DST', 'DBT', 'CSIR', 'ICSSR', 'MoE', 
        'Industry Sponsored', 'University Funded', 'Self-Funded', 'Other'
    ]
    
    for value in funding_agencies:
        if not LookupTable.query.filter_by(lookup_type='funding_agency', lookup_value=value).first():
            lookup = LookupTable(lookup_type='funding_agency', lookup_value=value)
            db.session.add(lookup)
    
    db.session.commit()

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(debug=True, host='0.0.0.0', port=5000)  # Added app.run() for convenience
