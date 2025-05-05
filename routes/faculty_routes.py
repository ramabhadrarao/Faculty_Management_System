from flask import Blueprint, request, redirect, url_for
from controllers.faculty_controller import FacultyController
from middleware.auth_middleware import login_required, faculty_required, same_department_required

faculty_bp = Blueprint('faculty', __name__)

# Faculty dashboard
@faculty_bp.route('/dashboard')
@login_required
@faculty_required
def dashboard():
    return FacultyController.dashboard()

# Faculty profile management
@faculty_bp.route('/profile/create', methods=['GET', 'POST'])
@login_required
@faculty_required
def create_profile():
    return FacultyController.create_profile()

@faculty_bp.route('/profile/view/<int:faculty_id>')
@login_required
@same_department_required
def view_profile(faculty_id):
    return FacultyController.view_profile(faculty_id)

@faculty_bp.route('/profile/edit/<int:faculty_id>', methods=['GET', 'POST'])
@login_required
@same_department_required
def edit_profile(faculty_id):
    return FacultyController.edit_profile(faculty_id)

@faculty_bp.route('/profile/additional-details/<int:faculty_id>', methods=['GET', 'POST'])
@login_required
@same_department_required
def edit_additional_details(faculty_id):
    return FacultyController.edit_additional_details(faculty_id)

# Work experience management
@faculty_bp.route('/work-experience/<int:faculty_id>')
@login_required
@same_department_required
def manage_work_experience(faculty_id):
    return FacultyController.manage_work_experience(faculty_id)

@faculty_bp.route('/work-experience/add/<int:faculty_id>', methods=['GET', 'POST'])
@login_required
@same_department_required
def add_work_experience(faculty_id):
    return FacultyController.add_work_experience(faculty_id)

@faculty_bp.route('/work-experience/delete/<int:faculty_id>/<int:experience_id>')
@login_required
@same_department_required
def delete_work_experience(faculty_id, experience_id):
    return FacultyController.delete_work_experience(faculty_id, experience_id)

# Profile status management
@faculty_bp.route('/profile/freeze/<int:faculty_id>')
@login_required
@same_department_required
def freeze_profile(faculty_id):
    return FacultyController.freeze_profile(faculty_id)

@faculty_bp.route('/profile/unfreeze/<int:faculty_id>')
@login_required
@same_department_required
def unfreeze_profile(faculty_id):
    return FacultyController.unfreeze_profile(faculty_id)

@faculty_bp.route('/profile/approve/<int:faculty_id>')
@login_required
@same_department_required
def approve_profile(faculty_id):
    return FacultyController.approve_profile(faculty_id)