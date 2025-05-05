from flask import Blueprint, request, redirect, url_for
from controllers.admin_controller import AdminController
from middleware.auth_middleware import login_required, admin_required, principal_required

admin_bp = Blueprint('admin', __name__)

# Admin dashboard
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return AdminController.dashboard()

# User management
@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    return AdminController.manage_users()

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    return AdminController.edit_user(user_id)

@admin_bp.route('/users/delete/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    return AdminController.delete_user(user_id)

# Department management
@admin_bp.route('/departments')
@login_required
@admin_required
def manage_departments():
    return AdminController.manage_departments()

@admin_bp.route('/departments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_department():
    return AdminController.add_department()

@admin_bp.route('/departments/edit/<int:department_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_department(department_id):
    return AdminController.edit_department(department_id)

# Role management
@admin_bp.route('/roles')
@login_required
@admin_required
def manage_roles():
    return AdminController.manage_roles()

@admin_bp.route('/roles/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_role():
    return AdminController.add_role()

@admin_bp.route('/roles/edit/<int:role_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_role(role_id):
    return AdminController.edit_role(role_id)

# Faculty management
@admin_bp.route('/faculty/pending')
@login_required
def pending_approvals():
    return AdminController.pending_approvals()

@admin_bp.route('/faculty/frozen')
@login_required
def frozen_profiles():
    return AdminController.frozen_profiles()

@admin_bp.route('/faculty/report')
@login_required
def faculty_report():
    return AdminController.faculty_report()

@admin_bp.route('/faculty/assign-hod', methods=['GET', 'POST'])
@login_required
@admin_required
def assign_hod():
    return AdminController.assign_hod()