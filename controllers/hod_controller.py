from flask import current_app, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_required
from models.base import db
from models.faculty import Faculty
from models.department import Department
from models.user import User, Role, UserRole
from config.constants import UserRoles, ProfileStatus
from middleware.auth_middleware import hod_required


class HODController:
    """Controller for HOD-related operations."""
    
    @staticmethod
    def dashboard():
        """Display the HOD dashboard."""
        if not current_user.is_hod:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        # Get HOD's faculty profile
        hod_faculty = Faculty.query.filter_by(user_id=current_user.user_id).first()
        
        if not hod_faculty:
            flash('HOD profile not found. Please complete your faculty profile.', 'warning')
            return redirect(url_for('faculty.create_profile'))
            
        # Get department
        department = Department.query.get(hod_faculty.department_id)
        
        if not department:
            flash('Department not found', 'danger')
            return redirect(url_for('faculty.dashboard'))
            
        # Get all faculty in the department
        faculty_members = Faculty.query.filter_by(department_id=department.department_id).all()
        
        # Count faculty by status
        status_counts = {
            'total': len(faculty_members),
            'pending': sum(1 for f in faculty_members if f.profile_status == ProfileStatus.PENDING),
            'approved': sum(1 for f in faculty_members if f.profile_status == ProfileStatus.APPROVED),
            'frozen': sum(1 for f in faculty_members if f.profile_status == ProfileStatus.FROZEN),
            'unfrozen': sum(1 for f in faculty_members if f.profile_status == ProfileStatus.UNFROZEN)
        }
        
        # Get recent faculty registrations
        recent_faculty = Faculty.query.filter_by(department_id=department.department_id)\
                               .order_by(Faculty.created_at.desc())\
                               .limit(5)\
                               .all()
        
        return render_template('hod/dashboard.html',
                              hod=hod_faculty,
                              department=department,
                              faculty_members=faculty_members,
                              status_counts=status_counts,
                              recent_faculty=recent_faculty)
    
    @staticmethod
    def department_faculty():
        """Display all faculty in the HOD's department."""
        if not current_user.is_hod:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        # Get HOD's faculty profile
        hod_faculty = Faculty.query.filter_by(user_id=current_user.user_id).first()
        
        if not hod_faculty:
            flash('HOD profile not found. Please complete your faculty profile.', 'warning')
            return redirect(url_for('faculty.create_profile'))
            
        # Get department
        department = Department.query.get(hod_faculty.department_id)
        
        if not department:
            flash('Department not found', 'danger')
            return redirect(url_for('faculty.dashboard'))
            
        # Get all faculty in the department
        faculty_members = Faculty.query.filter_by(department_id=department.department_id).all()
        
        return render_template('hod/department_faculty.html',
                              department=department,
                              faculty_members=faculty_members)
    
    @staticmethod
    def pending_approvals():
        """Display faculty profiles pending approval."""
        if not current_user.is_hod:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        # Get HOD's faculty profile
        hod_faculty = Faculty.query.filter_by(user_id=current_user.user_id).first()
        
        if not hod_faculty:
            flash('HOD profile not found. Please complete your faculty profile.', 'warning')
            return redirect(url_for('faculty.create_profile'))
            
        # Get department
        department = Department.query.get(hod_faculty.department_id)
        
        if not department:
            flash('Department not found', 'danger')
            return redirect(url_for('faculty.dashboard'))
            
        # Get all pending faculty in the department
        pending_faculty = Faculty.query.filter_by(
            department_id=department.department_id,
            profile_status=ProfileStatus.PENDING
        ).all()
        
        return render_template('hod/pending_approvals.html',
                              department=department,
                              pending_faculty=pending_faculty)
    
    @staticmethod
    def frozen_profiles():
        """Display frozen faculty profiles."""
        if not current_user.is_hod:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        # Get HOD's faculty profile
        hod_faculty = Faculty.query.filter_by(user_id=current_user.user_id).first()
        
        if not hod_faculty:
            flash('HOD profile not found. Please complete your faculty profile.', 'warning')
            return redirect(url_for('faculty.create_profile'))
            
        # Get department
        department = Department.query.get(hod_faculty.department_id)
        
        if not department:
            flash('Department not found', 'danger')
            return redirect(url_for('faculty.dashboard'))
            
        # Get all frozen faculty in the department
        frozen_faculty = Faculty.query.filter_by(
            department_id=department.department_id,
            profile_status=ProfileStatus.FROZEN
        ).all()
        
        return render_template('hod/frozen_profiles.html',
                              department=department,
                              frozen_faculty=frozen_faculty)
    
    @staticmethod
    def department_report():
        """Generate a report of faculty in the department."""
        if not current_user.is_hod:
            flash('Access denied', 'danger')
            return redirect(url_for('auth.login'))
            
        # Get HOD's faculty profile
        hod_faculty = Faculty.query.filter_by(user_id=current_user.user_id).first()
        
        if not hod_faculty:
            flash('HOD profile not found. Please complete your faculty profile.', 'warning')
            return redirect(url_for('faculty.create_profile'))
            
        # Get department
        department = Department.query.get(hod_faculty.department_id)
        
        if not department:
            flash('Department not found', 'danger')
            return redirect(url_for('faculty.dashboard'))
            
        # Get all faculty in the department
        faculty_members = Faculty.query.filter_by(department_id=department.department_id).all()
        
        # Collect statistics
        total_publications = 0
        total_workshops = 0
        total_awards = 0
        total_projects = 0
        
        for faculty in faculty_members:
            # Count publications
            from models.faculty import ResearchPublication
            publications = ResearchPublication.query.filter_by(faculty_id=faculty.faculty_id).count()
            total_publications += publications
            
            # Count workshops
            from models.faculty import WorkshopSeminar
            workshops = WorkshopSeminar.query.filter_by(faculty_id=faculty.faculty_id).count()
            total_workshops += workshops
            
            # Count awards
            from models.faculty import HonoursAward
            awards = HonoursAward.query.filter_by(faculty_id=faculty.faculty_id).count()
            total_awards += awards
            
            # Count projects
            from models.faculty import ResearchConsultancy
            projects = ResearchConsultancy.query.filter_by(faculty_id=faculty.faculty_id).count()
            total_projects += projects
        
        # Calculate averages
        num_faculty = len(faculty_members)
        avg_publications = total_publications / num_faculty if num_faculty > 0 else 0
        avg_workshops = total_workshops / num_faculty if num_faculty > 0 else 0
        avg_awards = total_awards / num_faculty if num_faculty > 0 else 0
        avg_projects = total_projects / num_faculty if num_faculty > 0 else 0
        
        # Prepare report data
        report_data = {
            'department': department,
            'faculty_count': num_faculty,
            'total_publications': total_publications,
            'total_workshops': total_workshops,
            'total_awards': total_awards,
            'total_projects': total_projects,
            'avg_publications': avg_publications,
            'avg_workshops': avg_workshops,
            'avg_awards': avg_awards,
            'avg_projects': avg_projects
        }
        
        return render_template('hod/department_report.html', report=report_data, faculty_members=faculty_members)