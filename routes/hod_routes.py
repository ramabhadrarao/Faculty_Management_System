from flask import Blueprint, request, redirect, url_for
from controllers.hod_controller import HODController
from middleware.auth_middleware import login_required, hod_required

hod_bp = Blueprint('hod', __name__)

# HOD dashboard
@hod_bp.route('/dashboard')
@login_required
@hod_required
def dashboard():
    return HODController.dashboard()

# Faculty management
@hod_bp.route('/department/faculty')
@login_required
@hod_required
def department_faculty():
    return HODController.department_faculty()

@hod_bp.route('/department/pending-approvals')
@login_required
@hod_required
def pending_approvals():
    return HODController.pending_approvals()

@hod_bp.route('/department/frozen-profiles')
@login_required
@hod_required
def frozen_profiles():
    return HODController.frozen_profiles()

@hod_bp.route('/department/report')
@login_required
@hod_required
def department_report():
    return HODController.department_report()