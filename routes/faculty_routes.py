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

# routes/faculty_routes.py 
# Add these routes to the existing faculty_bp Blueprint

# Teaching Activities
@faculty_bp.route('/teaching/<int:faculty_id>')
@login_required
@same_department_required
def manage_teaching_activities(faculty_id):
    return FacultyController.manage_teaching_activities(faculty_id)

@faculty_bp.route('/teaching/add/<int:faculty_id>', methods=['GET', 'POST'])
@login_required
@same_department_required
def add_teaching_activity(faculty_id):
    return FacultyController.add_teaching_activity(faculty_id)

@faculty_bp.route('/teaching/delete/<int:faculty_id>/<int:activity_id>')
@login_required
@same_department_required
def delete_teaching_activity(faculty_id, activity_id):
    return FacultyController.delete_teaching_activity(faculty_id, activity_id)

# Research Publications
@faculty_bp.route('/publications/<int:faculty_id>')
@login_required
@same_department_required
def manage_publications(faculty_id):
    return FacultyController.manage_publications(faculty_id)

@faculty_bp.route('/publications/add/<int:faculty_id>', methods=['GET', 'POST'])
@login_required
@same_department_required
def add_publication(faculty_id):
    return FacultyController.add_publication(faculty_id)

# routes/faculty_routes.py (continued)

@faculty_bp.route('/publications/delete/<int:faculty_id>/<int:publication_id>')
@login_required
@same_department_required
def delete_publication(faculty_id, publication_id):
    return FacultyController.delete_publication(faculty_id, publication_id)

# Workshops and Seminars
@faculty_bp.route('/workshops/<int:faculty_id>')
@login_required
@same_department_required
def manage_workshops(faculty_id):
    return FacultyController.manage_workshops(faculty_id)

@faculty_bp.route('/workshops/add/<int:faculty_id>', methods=['GET', 'POST'])
@login_required
@same_department_required
def add_workshop(faculty_id):
    return FacultyController.add_workshop(faculty_id)

@faculty_bp.route('/workshops/delete/<int:faculty_id>/<int:workshop_id>')
@login_required
@same_department_required
def delete_workshop(faculty_id, workshop_id):
    return FacultyController.delete_workshop(faculty_id, workshop_id)

# FDP/MDP Programs
@faculty_bp.route('/fdp-mdp/<int:faculty_id>')
@login_required
@same_department_required
def manage_mdp_fdp(faculty_id):
    return FacultyController.manage_mdp_fdp(faculty_id)

@faculty_bp.route('/fdp-mdp/add/<int:faculty_id>', methods=['GET', 'POST'])
@login_required
@same_department_required
def add_mdp_fdp(faculty_id):
    return FacultyController.add_mdp_fdp(faculty_id)

@faculty_bp.route('/fdp-mdp/delete/<int:faculty_id>/<int:program_id>')
@login_required
@same_department_required
def delete_mdp_fdp(faculty_id, program_id):
    return FacultyController.delete_mdp_fdp(faculty_id, program_id)

# Honours and Awards
@faculty_bp.route('/awards/<int:faculty_id>')
@login_required
@same_department_required
def manage_awards(faculty_id):
    return FacultyController.manage_awards(faculty_id)

@faculty_bp.route('/awards/add/<int:faculty_id>', methods=['GET', 'POST'])
@login_required
@same_department_required
def add_award(faculty_id):
    return FacultyController.add_award(faculty_id)

@faculty_bp.route('/awards/delete/<int:faculty_id>/<int:award_id>')
@login_required
@same_department_required
def delete_award(faculty_id, award_id):
    return FacultyController.delete_award(faculty_id, award_id)

# Research and Consultancy Projects
@faculty_bp.route('/projects/<int:faculty_id>')
@login_required
@same_department_required
def manage_projects(faculty_id):
    return FacultyController.manage_projects(faculty_id)

@faculty_bp.route('/projects/add/<int:faculty_id>', methods=['GET', 'POST'])
@login_required
@same_department_required
def add_project(faculty_id):
    return FacultyController.add_project(faculty_id)

@faculty_bp.route('/projects/delete/<int:faculty_id>/<int:project_id>')
@login_required
@same_department_required
def delete_project(faculty_id, project_id):
    return FacultyController.delete_project(faculty_id, project_id)