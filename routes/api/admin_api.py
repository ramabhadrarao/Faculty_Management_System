from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.base import db
from models.user import User, Role, UserRole
from models.faculty import Faculty
from models.department import Department, College
from config.constants import UserRoles, ProfileStatus
from datetime import datetime
import json

admin_api_bp = Blueprint('admin_api', __name__)

@admin_api_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    """API endpoint to get admin dashboard statistics."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check if user is admin or principal
    if not (user.is_admin or user.is_principal):
        return jsonify({"error": "Access denied"}), 403
    
    # Get counts for dashboard stats
    faculty_count = Faculty.query.count()
    department_count = Department.query.count()
    pending_count = Faculty.query.filter_by(profile_status=ProfileStatus.PENDING).count()
    frozen_count = Faculty.query.filter_by(profile_status=ProfileStatus.FROZEN).count()
    
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
    
    # Get recent faculty registrations
    recent_faculty = Faculty.query.order_by(Faculty.created_at.desc()).limit(5).all()
    recent_faculty_list = []
    
    for faculty in recent_faculty:
        recent_faculty_list.append({
            "faculty_id": faculty.faculty_id,
            "name": faculty.full_name,
            "email": faculty.email,
            "department": Department.query.get(faculty.department_id).department_name if faculty.department_id else None,
            "status": faculty.profile_status,
            "created_at": faculty.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    stats = {
        "faculty_count": faculty_count,
        "department_count": department_count,
        "pending_count": pending_count,
        "frozen_count": frozen_count,
        "role_distribution": role_distribution,
        "recent_faculty": recent_faculty_list
    }
    
    return jsonify(stats), 200

@admin_api_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """API endpoint to get all users."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check if user is admin
    if not user.is_admin:
        return jsonify({"error": "Access denied"}), 403
    
    # Get all users
    users = User.query.all()
    user_list = []
    
    for u in users:
        user_list.append({
            "user_id": u.user_id,
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "is_active": u.is_active,
            "roles": [role.name for role in u.roles],
            "created_at": u.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(user_list), 200

@admin_api_bp.route('/departments', methods=['GET'])
@jwt_required()
def get_departments():
    """API endpoint to get all departments."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check if user is admin or principal
    if not (user.is_admin or user.is_principal):
        return jsonify({"error": "Access denied"}), 403
    
    # Get all departments
    departments = Department.query.all()
    department_list = []
    
    for dept in departments:
        department_list.append({
            "department_id": dept.department_id,
            "department_name": dept.department_name,
            "department_code": dept.department_code,
            "college": College.query.get(dept.college_id).college_name if dept.college_id else None,
            "faculty_count": Faculty.query.filter_by(department_id=dept.department_id).count(),
            "logo": dept.logo
        })
    
    return jsonify(department_list), 200

@admin_api_bp.route('/pending-approvals', methods=['GET'])
@jwt_required()
def get_pending_approvals():
    """API endpoint to get faculty profiles pending approval."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check if user is admin, principal or HOD
    if not (user.is_admin or user.is_principal or user.is_hod):
        return jsonify({"error": "Access denied"}), 403
    
    # For HODs, filter by department
    if user.is_hod and not (user.is_admin or user.is_principal):
        # Get HOD's faculty profile
        hod_faculty = Faculty.query.filter_by(user_id=current_user_id).first()
        
        if not hod_faculty:
            return jsonify({"error": "HOD profile not found"}), 404
        
        # Get pending faculty in the HOD's department
        pending_faculty = Faculty.query.filter_by(
            department_id=hod_faculty.department_id,
            profile_status=ProfileStatus.PENDING
        ).all()
    else:
        # Get all pending faculty for admin/principal
        pending_faculty = Faculty.query.filter_by(profile_status=ProfileStatus.PENDING).all()
    
    # Format response
    pending_list = []
    for faculty in pending_faculty:
        pending_list.append({
            "faculty_id": faculty.faculty_id,
            "name": faculty.full_name,
            "email": faculty.email,
            "department": Department.query.get(faculty.department_id).department_name if faculty.department_id else None,
            "join_date": faculty.join_date.strftime('%Y-%m-%d'),
            "created_at": faculty.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(pending_list), 200

@admin_api_bp.route('/approve-profile/<int:faculty_id>', methods=['POST'])
@jwt_required()
def approve_profile(faculty_id):
    """API endpoint to approve a faculty profile."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check if user is admin, principal or HOD
    if not (user.is_admin or user.is_principal or user.is_hod):
        return jsonify({"error": "Access denied"}), 403
    
    # Get faculty profile
    faculty = Faculty.query.get(faculty_id)
    
    if not faculty:
        return jsonify({"error": "Faculty profile not found"}), 404
    
    # For HODs, check if in same department
    if user.is_hod and not (user.is_admin or user.is_principal):
        # Get HOD's faculty profile
        hod_faculty = Faculty.query.filter_by(user_id=current_user_id).first()
        
        if not hod_faculty:
            return jsonify({"error": "HOD profile not found"}), 404
        
        if hod_faculty.department_id != faculty.department_id:
            return jsonify({"error": "You can only approve faculty in your department"}), 403
    
    # Approve profile
    faculty.approve_profile()
    
    return jsonify({
        "message": "Faculty profile approved successfully"
    }), 200

@admin_api_bp.route('/unfreeze-profile/<int:faculty_id>', methods=['POST'])
@jwt_required()
def unfreeze_profile(faculty_id):
    """API endpoint to unfreeze a faculty profile."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check if user is admin, principal or HOD
    if not (user.is_admin or user.is_principal or user.is_hod):
        return jsonify({"error": "Access denied"}), 403
    
    # Get faculty profile
    faculty = Faculty.query.get(faculty_id)
    
    if not faculty:
        return jsonify({"error": "Faculty profile not found"}), 404
    
    # For HODs, check if in same department
    if user.is_hod and not (user.is_admin or user.is_principal):
        # Get HOD's faculty profile
        hod_faculty = Faculty.query.filter_by(user_id=current_user_id).first()
        
        if not hod_faculty:
            return jsonify({"error": "HOD profile not found"}), 404
        
        if hod_faculty.department_id != faculty.department_id:
            return jsonify({"error": "You can only unfreeze faculty in your department"}), 403
    
    # Unfreeze profile
    faculty.unfreeze_profile()
    
    return jsonify({
        "message": "Faculty profile unfrozen successfully"
    }), 200