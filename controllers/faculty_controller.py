import os
from datetime import datetime
from flask import current_app, flash, redirect, render_template, request, url_for, jsonify, abort
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from models.base import db
from models.faculty import (
    Faculty, FacultyAdditionalDetails, WorkExperience, TeachingActivity,
    ResearchPublication, WorkshopSeminar, MDPFDP, HonoursAward,
    ResearchConsultancy, Activity
)
from models.attachment import Attachment
from models.department import Department, College
from models.user import User
from config.constants import ProfileStatus, Visibility, ExperienceTypes
from middleware.auth_middleware import faculty_required


class FacultyController:
    """Controller for faculty-related operations."""
    
    @staticmethod
    def dashboard():
        """Display the faculty dashboard."""
        if not current_user.is_faculty:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        # Get faculty profile
        faculty = Faculty.query.filter_by(user_id=current_user.user_id).first()
        
        # If faculty profile doesn't exist, redirect to create profile
        if not faculty:
            flash('Please complete your faculty profile', 'warning')
            return redirect(url_for('faculty.create_profile'))
            
        # Count different entries for dashboard statistics
        stats = {
            'publications': ResearchPublication.query.filter_by(faculty_id=faculty.faculty_id).count(),
            'teaching': TeachingActivity.query.filter_by(faculty_id=faculty.faculty_id).count(),
            'workshops': WorkshopSeminar.query.filter_by(faculty_id=faculty.faculty_id).count(),
            'fdp_mdp': MDPFDP.query.filter_by(faculty_id=faculty.faculty_id).count(),
            'awards': HonoursAward.query.filter_by(faculty_id=faculty.faculty_id).count(),
            'projects': ResearchConsultancy.query.filter_by(faculty_id=faculty.faculty_id).count(),
            'activities': Activity.query.filter_by(faculty_id=faculty.faculty_id).count()
        }
        
        # Get recent activities for dashboard display
        recent_activities = Activity.query.filter_by(faculty_id=faculty.faculty_id) \
                                         .order_by(Activity.created_at.desc()) \
                                         .limit(5) \
                                         .all()
        
        return render_template('faculty/dashboard.html', 
                              faculty=faculty, 
                              stats=stats, 
                              recent_activities=recent_activities)
    
    @staticmethod
    def create_profile():
        """Create a new faculty profile."""
        if not current_user.is_faculty:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        # Check if faculty profile already exists
        existing_profile = Faculty.query.filter_by(user_id=current_user.user_id).first()
        if existing_profile:
            flash('Faculty profile already exists', 'warning')
            return redirect(url_for('faculty.view_profile', faculty_id=existing_profile.faculty_id))
            
        if request.method == 'POST':
            # Get form data
            regdno = request.form.get('regdno')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            gender = request.form.get('gender')
            dob = request.form.get('dob')
            contact_no = request.form.get('contact_no')
            email = request.form.get('email')
            address = request.form.get('address')
            join_date = request.form.get('join_date')
            department_id = request.form.get('department_id')
            
            # Validation
            if not regdno or not first_name or not email or not join_date or not department_id:
                flash('Please fill all required fields', 'danger')
                # Get departments for dropdown
                departments = Department.query.all()
                return render_template('faculty/create_profile.html', departments=departments)
                
            # Check if registration number already exists
            if Faculty.query.filter_by(regdno=regdno).first():
                flash('Registration number already exists', 'danger')
                departments = Department.query.all()
                return render_template('faculty/create_profile.html', departments=departments)
                
            # Create new faculty profile
            faculty = Faculty(
                user_id=current_user.user_id,
                regdno=regdno,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                dob=datetime.strptime(dob, '%Y-%m-%d') if dob else None,
                contact_no=contact_no,
                email=email,
                address=address,
                join_date=datetime.strptime(join_date, '%Y-%m-%d'),
                department_id=department_id,
                profile_status=ProfileStatus.PENDING
            )
            
            # Handle file uploads
            if 'photo' in request.files and request.files['photo'].filename:
                photo_file = request.files['photo']
                photo_attachment = FacultyController._save_attachment(photo_file, 'gallery_image')
                faculty.photo_attachment_id = photo_attachment.attachment_id
                
            if 'aadhar' in request.files and request.files['aadhar'].filename:
                aadhar_file = request.files['aadhar']
                aadhar_attachment = FacultyController._save_attachment(aadhar_file, 'attachment')
                faculty.aadhar_attachment_id = aadhar_attachment.attachment_id
                
            if 'pan' in request.files and request.files['pan'].filename:
                pan_file = request.files['pan']
                pan_attachment = FacultyController._save_attachment(pan_file, 'attachment')
                faculty.pan_attachment_id = pan_attachment.attachment_id
            
            db.session.add(faculty)
            db.session.commit()
            
            # Create empty additional details
            additional_details = FacultyAdditionalDetails(faculty_id=faculty.faculty_id)
            db.session.add(additional_details)
            db.session.commit()
            
            flash('Faculty profile created successfully', 'success')
            return redirect(url_for('faculty.view_profile', faculty_id=faculty.faculty_id))
        
        # Get departments for dropdown
        departments = Department.query.all()
        return render_template('faculty/create_profile.html', departments=departments)
    
    @staticmethod
    def view_profile(faculty_id):
        """View a faculty profile."""
        faculty = Faculty.query.get_or_404(faculty_id)
        
        # Only allow viewing if current user is the faculty member, an admin, a principal,
        # or an HOD of the same department
        if current_user.is_admin or current_user.is_principal:
            # Admins and principals can view all profiles
            pass
        elif current_user.is_hod:
            # HODs can only view faculty in their department
            hod_faculty = Faculty.query.filter_by(user_id=current_user.user_id).first()
            if not hod_faculty or hod_faculty.department_id != faculty.department_id:
                flash('You can only view faculty in your department', 'danger')
                return redirect(url_for('faculty.dashboard'))
        elif current_user.is_faculty:
            # Faculty can only view their own profile
            if faculty.user_id != current_user.user_id:
                flash('You can only view your own profile', 'danger')
                return redirect(url_for('faculty.dashboard'))
        else:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
        
        # Get related data
        additional_details = FacultyAdditionalDetails.query.filter_by(faculty_id=faculty_id).first()
        work_experiences = WorkExperience.query.filter_by(faculty_id=faculty_id).all()
        teaching_activities = TeachingActivity.query.filter_by(faculty_id=faculty_id).all()
        research_publications = ResearchPublication.query.filter_by(faculty_id=faculty_id).all()
        workshops_seminars = WorkshopSeminar.query.filter_by(faculty_id=faculty_id).all()
        mdp_fdp = MDPFDP.query.filter_by(faculty_id=faculty_id).all()
        honours_awards = HonoursAward.query.filter_by(faculty_id=faculty_id).all()
        research_consultancy = ResearchConsultancy.query.filter_by(faculty_id=faculty_id).all()
        activities = Activity.query.filter_by(faculty_id=faculty_id).all()
        
        return render_template('faculty/view_profile.html',
                              faculty=faculty,
                              additional_details=additional_details,
                              work_experiences=work_experiences,
                              teaching_activities=teaching_activities,
                              research_publications=research_publications,
                              workshops_seminars=workshops_seminars,
                              mdp_fdp=mdp_fdp,
                              honours_awards=honours_awards,
                              research_consultancy=research_consultancy,
                              activities=activities)
    
    @staticmethod
    def edit_profile(faculty_id):
        """Edit a faculty profile."""
        faculty = Faculty.query.get_or_404(faculty_id)
        
        # Check permissions
        if current_user.is_faculty and faculty.user_id != current_user.user_id:
            flash('You can only edit your own profile', 'danger')
            return redirect(url_for('faculty.dashboard'))
            
        # Check if profile is frozen
        if not faculty.can_edit():
            flash('This profile is currently frozen and cannot be edited', 'warning')
            return redirect(url_for('faculty.view_profile', faculty_id=faculty_id))
        
        if request.method == 'POST':
            # Update basic profile
            faculty.first_name = request.form.get('first_name')
            faculty.last_name = request.form.get('last_name')
            faculty.gender = request.form.get('gender')
            faculty.dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d') if request.form.get('dob') else None
            faculty.contact_no = request.form.get('contact_no')
            faculty.email = request.form.get('email')
            faculty.address = request.form.get('address')
            
            # Handle file uploads
            if 'photo' in request.files and request.files['photo'].filename:
                photo_file = request.files['photo']
                if faculty.photo_attachment_id:
                    # Update existing attachment
                    FacultyController._update_attachment(faculty.photo_attachment_id, photo_file)
                else:
                    # Create new attachment
                    photo_attachment = FacultyController._save_attachment(photo_file, 'gallery_image')
                    faculty.photo_attachment_id = photo_attachment.attachment_id
                
            if 'aadhar' in request.files and request.files['aadhar'].filename:
                aadhar_file = request.files['aadhar']
                if faculty.aadhar_attachment_id:
                    # Update existing attachment
                    FacultyController._update_attachment(faculty.aadhar_attachment_id, aadhar_file)
                else:
                    # Create new attachment
                    aadhar_attachment = FacultyController._save_attachment(aadhar_file, 'attachment')
                    faculty.aadhar_attachment_id = aadhar_attachment.attachment_id
                
            if 'pan' in request.files and request.files['pan'].filename:
                pan_file = request.files['pan']
                if faculty.pan_attachment_id:
                    # Update existing attachment
                    FacultyController._update_attachment(faculty.pan_attachment_id, pan_file)
                else:
                    # Create new attachment
                    pan_attachment = FacultyController._save_attachment(pan_file, 'attachment')
                    faculty.pan_attachment_id = pan_attachment.attachment_id
            
            # Update profile status if it was pending
            if faculty.profile_status == ProfileStatus.PENDING:
                faculty.profile_status = ProfileStatus.UNFROZEN
                
            db.session.commit()
            
            flash('Profile updated successfully', 'success')
            return redirect(url_for('faculty.view_profile', faculty_id=faculty_id))
        
        # Get departments for dropdown
        departments = Department.query.all()
        return render_template('faculty/edit_profile.html', faculty=faculty, departments=departments)
    
    @staticmethod
    def edit_additional_details(faculty_id):
        """Edit faculty additional details."""
        faculty = Faculty.query.get_or_404(faculty_id)
        
        # Check permissions
        if current_user.is_faculty and faculty.user_id != current_user.user_id:
            flash('You can only edit your own profile', 'danger')
            return redirect(url_for('faculty.dashboard'))
            
        # Check if profile is frozen
        if not faculty.can_edit():
            flash('This profile is currently frozen and cannot be edited', 'warning')
            return redirect(url_for('faculty.view_profile', faculty_id=faculty_id))
        
        # Get or create additional details
        details = FacultyAdditionalDetails.query.filter_by(faculty_id=faculty_id).first()
        if not details:
            details = FacultyAdditionalDetails(faculty_id=faculty_id)
            db.session.add(details)
            db.session.commit()
        
        if request.method == 'POST':
            # Update additional details
            details.position = request.form.get('position')
            details.father_name = request.form.get('father_name')
            details.father_occupation = request.form.get('father_occupation')
            details.mother_name = request.form.get('mother_name')
            details.mother_occupation = request.form.get('mother_occupation')
            details.marital_status = request.form.get('marital_status')
            details.spouse_name = request.form.get('spouse_name')
            details.spouse_occupation = request.form.get('spouse_occupation')
            details.nationality = request.form.get('nationality')
            details.religion = request.form.get('religion')
            details.category = request.form.get('category')
            details.caste = request.form.get('caste')
            details.sub_caste = request.form.get('sub_caste')
            details.aadhar_no = request.form.get('aadhar_no')
            details.pan_no = request.form.get('pan_no')
            details.contact_no2 = request.form.get('contact_no2')
            details.blood_group = request.form.get('blood_group')
            details.permanent_address = request.form.get('permanent_address')
            details.correspondence_address = request.form.get('correspondence_address')
            details.scopus_author_id = request.form.get('scopus_author_id')
            details.orcid_id = request.form.get('orcid_id')
            details.google_scholar_id_link = request.form.get('google_scholar_id_link')
            details.aicte_id = request.form.get('aicte_id')
            details.scet_id = request.form.get('scet_id')
            
            db.session.commit()
            
            flash('Additional details updated successfully', 'success')
            return redirect(url_for('faculty.view_profile', faculty_id=faculty_id))
        
        return render_template('faculty/edit_additional_details.html', faculty=faculty, details=details)
    
    @staticmethod
    def manage_work_experience(faculty_id):
        """Manage work experience entries."""
        faculty = Faculty.query.get_or_404(faculty_id)
        
        # Check permissions
        if current_user.is_faculty and faculty.user_id != current_user.user_id:
            flash('You can only manage your own work experience', 'danger')
            return redirect(url_for('faculty.dashboard'))
            
        # Check if profile is frozen
        if not faculty.can_edit():
            flash('This profile is currently frozen and cannot be edited', 'warning')
            return redirect(url_for('faculty.view_profile', faculty_id=faculty_id))
        
        # Get existing work experiences
        experiences = WorkExperience.query.filter_by(faculty_id=faculty_id).all()
        
        return render_template('faculty/manage_work_experience.html', 
                              faculty=faculty, 
                              experiences=experiences,
                              experience_types=[ExperienceTypes.TEACHING, ExperienceTypes.INDUSTRY])
    
    @staticmethod
    def add_work_experience(faculty_id):
        """Add a new work experience entry."""
        faculty = Faculty.query.get_or_404(faculty_id)
        
        # Check permissions
        if current_user.is_faculty and faculty.user_id != current_user.user_id:
            flash('You can only add to your own profile', 'danger')
            return redirect(url_for('faculty.dashboard'))
            
        # Check if profile is frozen
        if not faculty.can_edit():
            flash('This profile is currently frozen and cannot be edited', 'warning')
            return redirect(url_for('faculty.view_profile', faculty_id=faculty_id))
        
        if request.method == 'POST':
            # Get form data
            institution_name = request.form.get('institution_name')
            experience_type = request.form.get('experience_type')
            designation = request.form.get('designation')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            responsibilities = request.form.get('responsibilities')
            
            # Validation
            if not institution_name or not experience_type:
                flash('Institution name and experience type are required', 'danger')
                return redirect(url_for('faculty.manage_work_experience', faculty_id=faculty_id))
            
            # Create new work experience
            experience = WorkExperience(
                faculty_id=faculty_id,
                institution_name=institution_name,
                experience_type=experience_type,
                designation=designation,
                from_date=datetime.strptime(from_date, '%Y-%m-%d') if from_date else None,
                to_date=datetime.strptime(to_date, '%Y-%m-%d') if to_date else None,
                responsibilities=responsibilities
            )
            
            # Calculate years of experience if both dates are provided
            if from_date and to_date:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
                delta = to_date_obj - from_date_obj
                experience.number_of_years = delta.days // 365
            
            # Handle service certificate upload
            if 'service_certificate' in request.files and request.files['service_certificate'].filename:
                certificate_file = request.files['service_certificate']
                certificate_attachment = FacultyController._save_attachment(certificate_file, 'attachment')
                experience.service_certificate_attachment_id = certificate_attachment.attachment_id
            
            db.session.add(experience)
            db.session.commit()
            
            flash('Work experience added successfully', 'success')
            return redirect(url_for('faculty.manage_work_experience', faculty_id=faculty_id))
        
        return render_template('faculty/add_work_experience.html', 
                              faculty=faculty,
                              experience_types=[ExperienceTypes.TEACHING, ExperienceTypes.INDUSTRY])
    
    @staticmethod
    def delete_work_experience(faculty_id, experience_id):
        """Delete a work experience entry."""
        faculty = Faculty.query.get_or_404(faculty_id)
        experience = WorkExperience.query.get_or_404(experience_id)
        
        # Check if experience belongs to the faculty
        if experience.faculty_id != faculty.faculty_id:
            flash('Invalid work experience', 'danger')
            return redirect(url_for('faculty.manage_work_experience', faculty_id=faculty_id))
        
        # Check permissions
        if current_user.is_faculty and faculty.user_id != current_user.user_id:
            flash('You can only delete your own work experience', 'danger')
            return redirect(url_for('faculty.dashboard'))
            
        # Check if profile is frozen
        if not faculty.can_edit():
            flash('This profile is currently frozen and cannot be edited', 'warning')
            return redirect(url_for('faculty.view_profile', faculty_id=faculty_id))
        
        # Delete attachment if exists
        if experience.service_certificate_attachment_id:
            attachment = Attachment.query.get(experience.service_certificate_attachment_id)
            if attachment:
                FacultyController._delete_attachment(attachment)
        
        # Delete work experience
        db.session.delete(experience)
        db.session.commit()
        
        flash('Work experience deleted successfully', 'success')
        return redirect(url_for('faculty.manage_work_experience', faculty_id=faculty_id))
    
    @staticmethod
    def freeze_profile(faculty_id):
        """Freeze a faculty profile to prevent further editing."""
        faculty = Faculty.query.get_or_404(faculty_id)
        
        # Check permissions
        if current_user.is_faculty and faculty.user_id != current_user.user_id:
            flash('You can only freeze your own profile', 'danger')
            return redirect(url_for('faculty.dashboard'))
        
        # Freeze profile
        faculty.freeze_profile()
        
        flash('Profile has been frozen. It can no longer be edited until unfrozen by an administrator or HOD.', 'success')
        return redirect(url_for('faculty.view_profile', faculty_id=faculty_id))
    
    @staticmethod
    def unfreeze_profile(faculty_id):
        """Unfreeze a faculty profile to allow editing."""
        faculty = Faculty.query.get_or_404(faculty_id)
        
        # Check permissions - only admins, principals, and HODs can unfreeze profiles
        if current_user.is_faculty and not (current_user.is_admin or current_user.is_principal or current_user.is_hod):
            flash('Only administrators and HODs can unfreeze profiles', 'danger')
            return redirect(url_for('faculty.dashboard'))
            
        # For HODs, check if they're in the same department
        if current_user.is_hod and not current_user.is_admin and not current_user.is_principal:
            hod_faculty = Faculty.query.filter_by(user_id=current_user.user_id).first()
            if not hod_faculty or hod_faculty.department_id != faculty.department_id:
                flash('You can only unfreeze faculty in your department', 'danger')
                return redirect(url_for('faculty.dashboard'))
        
        # Unfreeze profile
        faculty.unfreeze_profile()
        
        flash('Profile has been unfrozen. It can now be edited.', 'success')
        return redirect(url_for('faculty.view_profile', faculty_id=faculty_id))
    
    @staticmethod
    def approve_profile(faculty_id):
        """Approve a faculty profile."""
        faculty = Faculty.query.get_or_404(faculty_id)
        
        # Check permissions - only admins, principals, and HODs can approve profiles
        if not (current_user.is_admin or current_user.is_principal or current_user.is_hod):
            flash('Only administrators and HODs can approve profiles', 'danger')
            return redirect(url_for('faculty.dashboard'))
            
        # For HODs, check if they're in the same department
        if current_user.is_hod and not current_user.is_admin and not current_user.is_principal:
            hod_faculty = Faculty.query.filter_by(user_id=current_user.user_id).first()
            if not hod_faculty or hod_faculty.department_id != faculty.department_id:
                flash('You can only approve faculty in your department', 'danger')
                return redirect(url_for('faculty.dashboard'))
        
        # Approve profile
        faculty.approve_profile()
        
        flash('Profile has been approved', 'success')
        return redirect(url_for('faculty.view_profile', faculty_id=faculty_id))
    
    # Helper methods for file attachments
    
    @staticmethod
    def _save_attachment(file_obj, attachment_type):
        """Save a file attachment and return the attachment object."""
        filename = secure_filename(file_obj.filename)
        # Create unique filename by adding timestamp
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        
        # Create upload directory if it doesn't exist
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        # Save file
        file_path = os.path.join(upload_folder, unique_filename)
        file_obj.save(file_path)
        
        # Create attachment record
        attachment = Attachment(
            file_path=unique_filename,
            attachment_type=attachment_type
        )
        db.session.add(attachment)
        db.session.commit()
        
        return attachment
    
    @staticmethod
    def _update_attachment(attachment_id, file_obj):
        """Update an existing attachment with a new file."""
        attachment = Attachment.query.get_or_404(attachment_id)
        
        # Delete old file
        old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], attachment.file_path)
        if os.path.exists(old_file_path):
            os.remove(old_file_path)
            
        # Save new file
        filename = secure_filename(file_obj.filename)
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file_obj.save(file_path)
        
        # Update attachment record
        attachment.file_path = unique_filename
        attachment.uploaded_at = datetime.utcnow()
        db.session.commit()
        
        return attachment
    
    @staticmethod
    def _delete_attachment(attachment):
        """Delete an attachment and its file."""
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], attachment.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        db.session.delete(attachment)
        db.session.commit()