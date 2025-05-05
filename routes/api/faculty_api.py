from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.base import db
from models.user import User
from models.faculty import (
    Faculty, FacultyAdditionalDetails, WorkExperience, TeachingActivity,
    ResearchPublication, WorkshopSeminar, MDPFDP, HonoursAward,
    ResearchConsultancy, Activity
)
from models.department import Department
from config.constants import ProfileStatus, ExperienceTypes
from datetime import datetime

faculty_api_bp = Blueprint('faculty_api', __name__)

@faculty_api_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """API endpoint to get faculty profile."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get faculty profile
    faculty = Faculty.query.filter_by(user_id=current_user_id).first()
    
    if not faculty:
        return jsonify({"message": "Faculty profile not created yet"}), 404
    
    # Get additional details
    additional_details = FacultyAdditionalDetails.query.filter_by(faculty_id=faculty.faculty_id).first()
    
    # Get department
    department = None
    if faculty.department_id:
        department = Department.query.get(faculty.department_id)
    
    # Format response
    profile = {
        "faculty_id": faculty.faculty_id,
        "regdno": faculty.regdno,
        "name": faculty.full_name,
        "gender": faculty.gender,
        "dob": faculty.dob.strftime('%Y-%m-%d') if faculty.dob else None,
        "contact_no": faculty.contact_no,
        "email": faculty.email,
        "address": faculty.address,
        "join_date": faculty.join_date.strftime('%Y-%m-%d'),
        "is_active": faculty.is_active,
        "edit_enabled": faculty.edit_enabled,
        "profile_status": faculty.profile_status,
        "department": department.department_name if department else None,
        "photo_url": f"/static/uploads/{faculty.photo_attachment.file_path}" if faculty.photo_attachment_id else None,
        "additional_details": {} if not additional_details else {
            "position": additional_details.position,
            "father_name": additional_details.father_name,
            "mother_name": additional_details.mother_name,
            "marital_status": additional_details.marital_status,
            "nationality": additional_details.nationality,
            "religion": additional_details.religion,
            "category": additional_details.category,
            "aadhar_no": additional_details.aadhar_no,
            "pan_no": additional_details.pan_no,
            "blood_group": additional_details.blood_group,
            "contact_no2": additional_details.contact_no2,
            "scopus_author_id": additional_details.scopus_author_id,
            "orcid_id": additional_details.orcid_id,
            "google_scholar_id_link": additional_details.google_scholar_id_link
        }
    }
    
    return jsonify(profile), 200

@faculty_api_bp.route('/profile', methods=['POST'])
@jwt_required()
def create_profile():
    """API endpoint to create faculty profile."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check if profile already exists
    existing_profile = Faculty.query.filter_by(user_id=current_user_id).first()
    if existing_profile:
        return jsonify({"error": "Faculty profile already exists"}), 400
    
    # Validate request
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    data = request.json
    required_fields = ['regdno', 'first_name', 'email', 'join_date', 'department_id']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create faculty profile
    faculty = Faculty(
        user_id=current_user_id,
        regdno=data['regdno'],
        first_name=data['first_name'],
        last_name=data.get('last_name'),
        gender=data.get('gender'),
        dob=datetime.strptime(data['dob'], '%Y-%m-%d') if 'dob' in data else None,
        contact_no=data.get('contact_no'),
        email=data['email'],
        address=data.get('address'),
        join_date=datetime.strptime(data['join_date'], '%Y-%m-%d'),
        department_id=data['department_id'],
        profile_status=ProfileStatus.PENDING
    )
    
    db.session.add(faculty)
    db.session.commit()
    
    # Create empty additional details
    additional_details = FacultyAdditionalDetails(faculty_id=faculty.faculty_id)
    db.session.add(additional_details)
    db.session.commit()
    
    return jsonify({
        "message": "Faculty profile created successfully",
        "faculty_id": faculty.faculty_id
    }), 201

@faculty_api_bp.route('/profile/<int:faculty_id>', methods=['PUT'])
@jwt_required()
def update_profile(faculty_id):
    """API endpoint to update faculty profile."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get faculty profile
    faculty = Faculty.query.get(faculty_id)
    
    if not faculty:
        return jsonify({"error": "Faculty profile not found"}), 404
    
    # Check permissions
    if faculty.user_id != current_user_id:
        return jsonify({"error": "You can only update your own profile"}), 403
    
    # Check if profile is frozen
    if not faculty.can_edit():
        return jsonify({"error": "This profile is currently frozen and cannot be edited"}), 403
    
    # Validate request
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    data = request.json
    
    # Update profile
    if 'first_name' in data:
        faculty.first_name = data['first_name']
    if 'last_name' in data:
        faculty.last_name = data['last_name']
    if 'gender' in data:
        faculty.gender = data['gender']
    if 'dob' in data:
        faculty.dob = datetime.strptime(data['dob'], '%Y-%m-%d')
    if 'contact_no' in data:
        faculty.contact_no = data['contact_no']
    if 'email' in data:
        faculty.email = data['email']
    if 'address' in data:
        faculty.address = data['address']
    
    # Update profile status if it was pending
    if faculty.profile_status == ProfileStatus.PENDING:
        faculty.profile_status = ProfileStatus.UNFROZEN
    
    db.session.commit()
    
    return jsonify({
        "message": "Faculty profile updated successfully"
    }), 200

@faculty_api_bp.route('/additional-details/<int:faculty_id>', methods=['PUT'])
@jwt_required()
def update_additional_details(faculty_id):
    """API endpoint to update faculty additional details."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get faculty profile
    faculty = Faculty.query.get(faculty_id)
    
    if not faculty:
        return jsonify({"error": "Faculty profile not found"}), 404
    
    # Check permissions
    if faculty.user_id != current_user_id:
        return jsonify({"error": "You can only update your own profile"}), 403
    
    # Check if profile is frozen
    if not faculty.can_edit():
        return jsonify({"error": "This profile is currently frozen and cannot be edited"}), 403
    
    # Validate request
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    data = request.json
    
    # Get or create additional details
    details = FacultyAdditionalDetails.query.filter_by(faculty_id=faculty_id).first()
    if not details:
        details = FacultyAdditionalDetails(faculty_id=faculty_id)
        db.session.add(details)
    
    # Update fields
    for field in data:
        if hasattr(details, field):
            setattr(details, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        "message": "Additional details updated successfully"
    }), 200

@faculty_api_bp.route('/work-experience/<int:faculty_id>', methods=['GET'])
@jwt_required()
def get_work_experiences(faculty_id):
    """API endpoint to get faculty work experiences."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get faculty profile
    faculty = Faculty.query.get(faculty_id)
    
    if not faculty:
        return jsonify({"error": "Faculty profile not found"}), 404
    
    # Get work experiences
    experiences = WorkExperience.query.filter_by(faculty_id=faculty_id).all()
    
    # Format response
    experience_list = []
    for exp in experiences:
        experience_list.append({
            "experience_id": exp.experience_id,
            "institution_name": exp.institution_name,
            "experience_type": exp.experience_type,
            "designation": exp.designation,
            "from_date": exp.from_date.strftime('%Y-%m-%d') if exp.from_date else None,
            "to_date": exp.to_date.strftime('%Y-%m-%d') if exp.to_date else None,
            "number_of_years": exp.number_of_years,
            "responsibilities": exp.responsibilities,
            "certificate_url": f"/static/uploads/{exp.service_certificate.file_path}" if exp.service_certificate_attachment_id else None
        })
    
    return jsonify(experience_list), 200

@faculty_api_bp.route('/work-experience/<int:faculty_id>', methods=['POST'])
@jwt_required()
def add_work_experience(faculty_id):
    """API endpoint to add faculty work experience."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get faculty profile
    faculty = Faculty.query.get(faculty_id)
    
    if not faculty:
        return jsonify({"error": "Faculty profile not found"}), 404
    
    # Check permissions
    if faculty.user_id != current_user_id:
        return jsonify({"error": "You can only add to your own profile"}), 403
    
    # Check if profile is frozen
    if not faculty.can_edit():
        return jsonify({"error": "This profile is currently frozen and cannot be edited"}), 403
    
    # Validate request
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    data = request.json
    required_fields = ['institution_name', 'experience_type']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create work experience
    experience = WorkExperience(
        faculty_id=faculty_id,
        institution_name=data['institution_name'],
        experience_type=data['experience_type'],
        designation=data.get('designation'),
        from_date=datetime.strptime(data['from_date'], '%Y-%m-%d') if 'from_date' in data else None,
        to_date=datetime.strptime(data['to_date'], '%Y-%m-%d') if 'to_date' in data else None,
        responsibilities=data.get('responsibilities')
    )
    
    # Calculate years of experience if both dates are provided
    if 'from_date' in data and 'to_date' in data:
        from_date_obj = datetime.strptime(data['from_date'], '%Y-%m-%d')
        to_date_obj = datetime.strptime(data['to_date'], '%Y-%m-%d')
        delta = to_date_obj - from_date_obj
        experience.number_of_years = delta.days // 365
    
    db.session.add(experience)
    db.session.commit()
    
    return jsonify({
        "message": "Work experience added successfully",
        "experience_id": experience.experience_id
    }), 201

@faculty_api_bp.route('/work-experience/<int:faculty_id>/<int:experience_id>', methods=['DELETE'])
@jwt_required()
def delete_work_experience(faculty_id, experience_id):
    """API endpoint to delete faculty work experience."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get faculty profile
    faculty = Faculty.query.get(faculty_id)
    
    if not faculty:
        return jsonify({"error": "Faculty profile not found"}), 404
    
    # Check permissions
    if faculty.user_id != current_user_id:
        return jsonify({"error": "You can only delete your own work experience"}), 403
    
    # Check if profile is frozen
    if not faculty.can_edit():
        return jsonify({"error": "This profile is currently frozen and cannot be edited"}), 403
    
    # Get work experience
    experience = WorkExperience.query.get(experience_id)
    
    if not experience or experience.faculty_id != faculty_id:
        return jsonify({"error": "Work experience not found"}), 404
    
    db.session.delete(experience)
    db.session.commit()
    
    return jsonify({
        "message": "Work experience deleted successfully"
    }), 200

@faculty_api_bp.route('/freeze/<int:faculty_id>', methods=['POST'])
@jwt_required()
def freeze_profile(faculty_id):
    """API endpoint to freeze faculty profile."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get faculty profile
    faculty = Faculty.query.get(faculty_id)
    
    if not faculty:
        return jsonify({"error": "Faculty profile not found"}), 404
    
    # Check permissions
    if faculty.user_id != current_user_id:
        return jsonify({"error": "You can only freeze your own profile"}), 403
    
    # Freeze profile
    faculty.freeze_profile()
    
    return jsonify({
        "message": "Profile has been frozen. It can no longer be edited until unfrozen by an administrator or HOD."
    }), 200
