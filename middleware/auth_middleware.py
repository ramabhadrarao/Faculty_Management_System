from functools import wraps
from flask import session, redirect, url_for, flash, request, abort
from flask_login import current_user
from models.user import User
from config.constants import UserRoles

def login_required(f):
    """Decorator for routes that require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator for routes that require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def principal_required(f):
    """Decorator for routes that require principal role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_principal:
            flash('You do not have permission to access this page', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def hod_required(f):
    """Decorator for routes that require HOD role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_hod:
            flash('You do not have permission to access this page', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def faculty_required(f):
    """Decorator for routes that require faculty role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_faculty:
            flash('You do not have permission to access this page', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission):
    """Decorator for routes that require specific permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page', 'warning')
                return redirect(url_for('auth.login', next=request.url))
                
            # Check if user has any role with the required permission
            has_permission = False
            for role in current_user.roles:
                if any(perm.name == permission for perm in role.permissions):
                    has_permission = True
                    break
                    
            if not has_permission:
                flash('You do not have permission to access this page', 'danger')
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def same_department_required(f):
    """
    Decorator for HOD routes that require the faculty to be in the same department.
    Used for HODs to access only their department's faculty.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login', next=request.url))
            
        faculty_id = kwargs.get('faculty_id')
        if not faculty_id:
            abort(400)  # Bad request if no faculty ID provided
            
        from models.faculty import Faculty
        from models.base import db
        
        # Get the target faculty's department
        target_faculty = Faculty.query.get_or_404(faculty_id)
        
        # Get the HOD's faculty profile and department
        hod_faculty = Faculty.query.filter_by(user_id=current_user.user_id).first()
        
        if not hod_faculty:
            flash('Your faculty profile is not set up properly', 'danger')
            abort(403)
            
        # Check if this is an admin or principal (they can access any department)
        if current_user.is_admin or current_user.is_principal:
            return f(*args, **kwargs)
            
        # For HODs, check if they're in the same department
        if current_user.is_hod and hod_faculty.department_id == target_faculty.department_id:
            return f(*args, **kwargs)
            
        # Allow faculty to access their own profile
        if current_user.is_faculty and target_faculty.user_id == current_user.user_id:
            return f(*args, **kwargs)
            
        flash('You do not have permission to access this faculty profile', 'danger')
        abort(403)
        
    return decorated_function