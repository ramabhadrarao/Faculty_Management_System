from flask import current_app, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_required
from models.base import db
from models.faculty import Faculty
from models.department import Department, College, Program, Branch
from models.user import User, Role, UserRole
from config.constants import UserRoles, ProfileStatus
from middleware.auth_middleware import admin_required, principal_required
from flask_wtf import FlaskForm

class AdminController:
    """Controller for admin-related operations."""
    
    @staticmethod
    def dashboard():
        """Display the admin dashboard."""
        if not (current_user.is_admin or current_user.is_principal):
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        # Get counts for dashboard stats
        faculty_count = Faculty.query.count()
        department_count = Department.query.count()
        pending_count = Faculty.query.filter_by(profile_status=ProfileStatus.PENDING).count()
        frozen_count = Faculty.query.filter_by(profile_status=ProfileStatus.FROZEN).count()
        
        # Get recent faculty registrations
        recent_faculty = Faculty.query.order_by(Faculty.created_at.desc()).limit(5).all()
        
        # Get roles distribution
        admin_count = UserRole.query.join(Role).filter(Role.name == UserRoles.ADMIN).count()
        principal_count = UserRole.query.join(Role).filter(Role.name == UserRoles.PRINCIPAL).count()
        hod_count = UserRole.query.join(Role).filter(Role.name == UserRoles.HOD).count()
        faculty_role_count = UserRole.query.join(Role).filter(Role.name == UserRoles.FACULTY).count()
        
        role_distribution = {
            'admin': admin_count,
            'principal': principal_count,
            'hod': hod_count,
            'faculty': faculty_role_count
        }
        
        return render_template('admin/dashboard.html',
                              faculty_count=faculty_count,
                              department_count=department_count,
                              pending_count=pending_count,
                              frozen_count=frozen_count,
                              recent_faculty=recent_faculty,
                              role_distribution=role_distribution)
    
    @staticmethod
    def manage_users():
        """Display and manage users."""
        if not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
        
        # Handle POST request for adding a new user
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            
            # Basic validation
            if not username or not email or not password:
                flash('All required fields must be filled out', 'danger')
                return redirect(url_for('admin.manage_users'))
                
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return redirect(url_for('admin.manage_users'))
            
            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return redirect(url_for('admin.manage_users'))
                
            if User.query.filter_by(email=email).first():
                flash('Email already exists', 'danger')
                return redirect(url_for('admin.manage_users'))
            
            # Create new user
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            user.password = password  # This will hash the password
            
            # Add roles if selected
            roles = Role.query.all()
            for role in roles:
                if request.form.get(f'role_{role.role_id}') == 'on':
                    user.roles.append(role)
            
            # If no roles selected, add faculty role by default
            if not user.roles:
                faculty_role = Role.query.filter_by(name=UserRoles.FACULTY).first()
                if faculty_role:
                    user.roles.append(faculty_role)
            
            db.session.add(user)
            db.session.commit()
            
            flash('User added successfully', 'success')
            return redirect(url_for('admin.manage_users'))
                
        # GET request - display users
        users = User.query.all()
        roles = Role.query.all()
        
        return render_template('admin/manage_users.html', users=users, roles=roles)
    @staticmethod
    def deactivate_user(user_id):
        """Deactivate a user."""
        if not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        user = User.query.get_or_404(user_id)
        
        # Prevent deactivating self
        if user.user_id == current_user.user_id:
            flash('You cannot deactivate your own account', 'danger')
            return redirect(url_for('admin.manage_users'))
        
        user.is_active = False
        db.session.commit()
        
        flash('User deactivated successfully', 'success')
        return redirect(url_for('admin.manage_users'))
    @staticmethod
    def activate_user(user_id):
        """Activate a user."""
        if not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        user = User.query.get_or_404(user_id)
        
        user.is_active = True
        db.session.commit()
        
        flash('User activated successfully', 'success')
        return redirect(url_for('admin.manage_users'))
    @staticmethod
    def reset_user_password(user_id):
        """Reset a user's password."""
        if not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        user = User.query.get_or_404(user_id)
        
        # Generate random password
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        new_password = ''.join(secrets.choice(alphabet) for i in range(10))
        
        # Set new password
        user.password = new_password
        db.session.commit()
        
        flash(f'Password reset successfully. New password: {new_password}', 'success')
        return redirect(url_for('admin.edit_user', user_id=user_id))
    @staticmethod
    def edit_user(user_id):
        """Edit a user's details and roles."""
        if not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        user = User.query.get_or_404(user_id)
        roles = Role.query.all()
        
        if request.method == 'POST':
            # Update user details
            user.username = request.form.get('username')
            user.email = request.form.get('email')
            user.first_name = request.form.get('first_name')
            user.last_name = request.form.get('last_name')
            user.is_active = request.form.get('is_active') == 'on'
            
            # Update password if provided
            new_password = request.form.get('new_password')
            if new_password:
                user.password = new_password
            
            # Update roles
            user.roles = []
            for role in roles:
                if request.form.get(f'role_{role.role_id}') == 'on':
                    user.roles.append(role)
            
            db.session.commit()
            
            flash('User updated successfully', 'success')
            return redirect(url_for('admin.manage_users'))
        
        return render_template('admin/edit_user.html', user=user, roles=roles)
    
    @staticmethod
    def delete_user(user_id):
        """Delete a user."""
        if not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting self
        if user.user_id == current_user.user_id:
            flash('You cannot delete your own account', 'danger')
            return redirect(url_for('admin.manage_users'))
        
        # Delete faculty profile if exists
        faculty = Faculty.query.filter_by(user_id=user.user_id).first()
        if faculty:
            db.session.delete(faculty)
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        flash('User deleted successfully', 'success')
        return redirect(url_for('admin.manage_users'))
    
    @staticmethod
    def manage_departments():
        """Display and manage departments."""
        if not (current_user.is_admin or current_user.is_principal):
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        departments = Department.query.all()
        colleges = College.query.all()
        
        return render_template('admin/manage_departments.html', departments=departments, colleges=colleges)
    
    @staticmethod
    def add_department():
        """Add a new department."""
        if not (current_user.is_admin or current_user.is_principal):
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
        # Create a simple form for CSRF protection
        class SimpleForm(FlaskForm):
            pass
        
        form = SimpleForm()
            
        if request.method == 'POST':
            department_name = request.form.get('department_name')
            department_code = request.form.get('department_code')
            college_id = request.form.get('college_id')
            
            # Validation
            if not department_name or not department_code or not college_id:
                flash('All fields are required', 'danger')
                return redirect(url_for('admin.manage_departments'))
            
            # Check if department code already exists
            if Department.query.filter_by(department_code=department_code).first():
                flash('Department code already exists', 'danger')
                return redirect(url_for('admin.manage_departments'))
            
            # Create department
            department = Department(
                department_name=department_name,
                department_code=department_code,
                college_id=college_id
            )
            
            # Handle logo upload
            if 'logo' in request.files and request.files['logo'].filename:
                from controllers.faculty_controller import FacultyController
                logo_file = request.files['logo']
                filename = FacultyController._save_attachment(logo_file, 'gallery_image').file_path
                department.logo = filename
            
            db.session.add(department)
            db.session.commit()
            
            flash('Department added successfully', 'success')
            return redirect(url_for('admin.manage_departments'))
        
        # Get colleges for dropdown
        colleges = College.query.all()
        return render_template('admin/add_department.html', colleges=colleges,form=form)
    
    @staticmethod
    def edit_department(department_id):
        """Edit a department."""
        if not (current_user.is_admin or current_user.is_principal):
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        department = Department.query.get_or_404(department_id)
        
        if request.method == 'POST':
            department.department_name = request.form.get('department_name')
            department.department_code = request.form.get('department_code')
            department.college_id = request.form.get('college_id')
            
            # Handle logo upload
            if 'logo' in request.files and request.files['logo'].filename:
                from controllers.faculty_controller import FacultyController
                logo_file = request.files['logo']
                filename = FacultyController._save_attachment(logo_file, 'gallery_image').file_path
                department.logo = filename
            
            db.session.commit()
            
            flash('Department updated successfully', 'success')
            return redirect(url_for('admin.manage_departments'))
        
        # Get colleges for dropdown
        colleges = College.query.all()
        return render_template('admin/edit_department.html', department=department, colleges=colleges)
    @staticmethod
    def delete_department(department_id):
        """Delete a department."""
        if not (current_user.is_admin or current_user.is_principal):
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        department = Department.query.get_or_404(department_id)
        
        # Check if department has faculty assigned
        faculty_count = Faculty.query.filter_by(department_id=department_id).count()
        if faculty_count > 0:
            flash(f'Cannot delete department with {faculty_count} faculty members assigned', 'danger')
            return redirect(url_for('admin.manage_departments'))
        
        # Delete department's logo if it exists
        if department.logo:
            from controllers.faculty_controller import FacultyController
            logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], department.logo)
            if os.path.exists(logo_path):
                os.remove(logo_path)
        
        # Delete department
        db.session.delete(department)
        db.session.commit()
        
        flash('Department deleted successfully', 'success')
        return redirect(url_for('admin.manage_departments'))
    @staticmethod
    def manage_roles():
        """Display and manage roles and permissions."""
        if not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        roles = Role.query.all()
        
        return render_template('admin/manage_roles.html', roles=roles)
    
    @staticmethod
    def add_role():
        """Add a new role."""
        if not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            
            # Validation
            if not name:
                flash('Role name is required', 'danger')
                return redirect(url_for('admin.manage_roles'))
            
            # Check if role already exists
            if Role.query.filter_by(name=name).first():
                flash('Role already exists', 'danger')
                return redirect(url_for('admin.manage_roles'))
            
            # Create role
            role = Role(name=name, description=description)
            db.session.add(role)
            db.session.commit()
            
            flash('Role added successfully', 'success')
            return redirect(url_for('admin.manage_roles'))
        
        return render_template('admin/add_role.html')
    
    @staticmethod
    def edit_role(role_id):
        """Edit a role."""
        if not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        role = Role.query.get_or_404(role_id)
        
        if request.method == 'POST':
            role.name = request.form.get('name')
            role.description = request.form.get('description')
            
            db.session.commit()
            
            flash('Role updated successfully', 'success')
            return redirect(url_for('admin.manage_roles'))
        
        return render_template('admin/edit_role.html', role=role)
    
    @staticmethod
    def pending_approvals():
        """Display all faculty profiles pending approval."""
        if not (current_user.is_admin or current_user.is_principal):
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        pending_faculty = Faculty.query.filter_by(profile_status=ProfileStatus.PENDING).all()
        
        return render_template('admin/pending_approvals.html', pending_faculty=pending_faculty)
    
    @staticmethod
    def frozen_profiles():
        """Display all frozen faculty profiles."""
        if not (current_user.is_admin or current_user.is_principal):
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        frozen_faculty = Faculty.query.filter_by(profile_status=ProfileStatus.FROZEN).all()
        
        return render_template('admin/frozen_profiles.html', frozen_faculty=frozen_faculty)
    
    @staticmethod
    def faculty_report():
        """Generate a report of all faculty."""
        if not (current_user.is_admin or current_user.is_principal):
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
        
        # Get faculty count by department
        departments = Department.query.all()
        department_stats = []
        
        for dept in departments:
            faculty_count = Faculty.query.filter_by(department_id=dept.department_id).count()
            department_stats.append({
                'department': dept,
                'faculty_count': faculty_count
            })
        
        # Get faculty count by status
        status_counts = {
            'total': Faculty.query.count(),
            'pending': Faculty.query.filter_by(profile_status=ProfileStatus.PENDING).count(),
            'approved': Faculty.query.filter_by(profile_status=ProfileStatus.APPROVED).count(),
            'frozen': Faculty.query.filter_by(profile_status=ProfileStatus.FROZEN).count(),
            'unfrozen': Faculty.query.filter_by(profile_status=ProfileStatus.UNFROZEN).count()
        }
        
        # Get recent activities
        from models.faculty import Activity
        recent_activities = Activity.query.order_by(Activity.created_at.desc()).limit(10).all()
        
        return render_template('admin/faculty_report.html',
                              department_stats=department_stats,
                              status_counts=status_counts,
                              recent_activities=recent_activities)
    @staticmethod
    def add_college():
        """Add a new college."""
        if not (current_user.is_admin or current_user.is_principal):
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        if request.method == 'POST':
            college_name = request.form.get('college_name')
            college_code = request.form.get('college_code')
            
            # Validation
            if not college_name or not college_code:
                flash('All fields are required', 'danger')
                return redirect(url_for('admin.manage_departments'))
            
            # Check if college code already exists
            if College.query.filter_by(college_code=college_code).first():
                flash('College code already exists', 'danger')
                return redirect(url_for('admin.manage_departments'))
            
            # Create college
            college = College(
                college_name=college_name,
                college_code=college_code
            )
            
            # Handle logo upload
            if 'logo' in request.files and request.files['logo'].filename:
                from controllers.faculty_controller import FacultyController
                logo_file = request.files['logo']
                filename = FacultyController._save_attachment(logo_file, 'gallery_image').file_path
                college.logo = filename
            
            db.session.add(college)
            db.session.commit()
            
            flash('College added successfully', 'success')
            return redirect(url_for('admin.manage_departments'))
        
        return render_template('admin/add_college.html')
    @staticmethod
    def assign_hod():
        """Assign faculty as HOD."""
        if not (current_user.is_admin or current_user.is_principal):
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
        # Create a simple form for CSRF protection
        class SimpleForm(FlaskForm):
            pass
        
        form = SimpleForm()
            
        if request.method == 'POST':
            faculty_id = request.form.get('faculty_id')
            
            # Validation
            if not faculty_id:
                flash('No faculty selected', 'danger')
                return redirect(url_for('admin.manage_departments'))
            
            # Get faculty
            faculty = Faculty.query.get_or_404(faculty_id)
            user = User.query.get(faculty.user_id)
            
            if not user:
                flash('User not found for this faculty', 'danger')
                return redirect(url_for('admin.manage_departments'))
            
            # Add HOD role
            hod_role = Role.query.filter_by(name=UserRoles.HOD).first()
            if not hod_role:
                flash('HOD role not found', 'danger')
                return redirect(url_for('admin.manage_departments'))
            
            if hod_role not in user.roles:
                user.roles.append(hod_role)
                db.session.commit()
                flash(f'{faculty.full_name} has been assigned as HOD', 'success')
            else:
                flash(f'{faculty.full_name} is already a HOD', 'info')
            
                return render_template('admin/assign_hod.html', departments=departments, faculty_by_dept=faculty_by_dept, form=form)

        
        # Get departments and faculty
        departments = Department.query.all()
        faculty_by_dept = {}
        
        for dept in departments:
            faculty_by_dept[dept.department_id] = Faculty.query.filter_by(department_id=dept.department_id).all()
        
        return render_template('admin/assign_hod.html', departments=departments, faculty_by_dept=faculty_by_dept)