from datetime import datetime
from models.base import db
from config.constants import ProfileStatus, Visibility, ExperienceTypes
from models.attachment import Attachment
from sqlalchemy import Enum


class Faculty(db.Model):
    """Faculty model based on the faculty table in the schema."""
    __tablename__ = 'faculty'
    
    faculty_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    regdno = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=True)
    dob = db.Column(db.Date)
    contact_no = db.Column(db.String(15))
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.Text)
    join_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    edit_enabled = db.Column(db.Boolean, default=True)
    profile_status = db.Column(db.Enum(ProfileStatus.PENDING, ProfileStatus.APPROVED, 
                                       ProfileStatus.FROZEN, ProfileStatus.UNFROZEN),
                               default=ProfileStatus.PENDING)
    aadhar_attachment_id = db.Column(db.Integer, db.ForeignKey('attachments.attachment_id'))
    pan_attachment_id = db.Column(db.Integer, db.ForeignKey('attachments.attachment_id'))
    photo_attachment_id = db.Column(db.Integer, db.ForeignKey('attachments.attachment_id'))
    visibility = db.Column(db.Enum(Visibility.SHOW, Visibility.HIDE), default=Visibility.SHOW)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('faculty_profile', uselist=False))
    department = db.relationship('Department', backref='faculty_members')
    aadhar_attachment = db.relationship('Attachment', foreign_keys=[aadhar_attachment_id])
    pan_attachment = db.relationship('Attachment', foreign_keys=[pan_attachment_id])
    photo_attachment = db.relationship('Attachment', foreign_keys=[photo_attachment_id])
    additional_details = db.relationship('FacultyAdditionalDetails', backref='faculty', uselist=False, cascade='all, delete-orphan')
    work_experiences = db.relationship('WorkExperience', backref='faculty', cascade='all, delete-orphan')
    teaching_activities = db.relationship('TeachingActivity', backref='faculty', cascade='all, delete-orphan')
    research_publications = db.relationship('ResearchPublication', backref='faculty', cascade='all, delete-orphan')
    workshops_seminars = db.relationship('WorkshopSeminar', backref='faculty', cascade='all, delete-orphan')
    mdp_fdp = db.relationship('MDPFDP', backref='faculty', cascade='all, delete-orphan')
    honours_awards = db.relationship('HonoursAward', backref='faculty', cascade='all, delete-orphan')
    research_consultancy = db.relationship('ResearchConsultancy', backref='faculty', cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='faculty', cascade='all, delete-orphan')
    
    @property
    def full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    def can_edit(self):
        """Check if faculty profile can be edited."""
        return self.edit_enabled and self.profile_status != ProfileStatus.FROZEN
    
    def freeze_profile(self):
        """Freeze faculty profile to prevent editing."""
        self.edit_enabled = False
        self.profile_status = ProfileStatus.FROZEN
        db.session.commit()
    
    def unfreeze_profile(self):
        """Unfreeze faculty profile to allow editing."""
        self.edit_enabled = True
        self.profile_status = ProfileStatus.UNFROZEN
        db.session.commit()
    
    def approve_profile(self):
        """Approve faculty profile."""
        self.profile_status = ProfileStatus.APPROVED
        db.session.commit()
    
    def __repr__(self):
        return f'<Faculty {self.full_name}>'


class FacultyAdditionalDetails(db.Model):
    """Faculty additional details model."""
    __tablename__ = 'faculty_additional_details'
    
    detail_id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=False)
    department = db.Column(db.String(255))
    position = db.Column(db.String(255))
    profilepic = db.Column(db.String(255))
    father_name = db.Column(db.String(255))
    father_occupation = db.Column(db.String(255))
    mother_name = db.Column(db.String(255))
    mother_occupation = db.Column(db.String(255))
    marital_status = db.Column(db.String(20))
    spouse_name = db.Column(db.String(255))
    spouse_occupation = db.Column(db.String(255))
    nationality = db.Column(db.String(255))
    religion = db.Column(db.String(255))
    category = db.Column(db.String(255))
    caste = db.Column(db.String(255))
    sub_caste = db.Column(db.String(255))
    aadhar_no = db.Column(db.String(20))
    pan_no = db.Column(db.String(20))
    contact_no2 = db.Column(db.String(20))
    blood_group = db.Column(db.String(10))
    permanent_address = db.Column(db.Text)
    correspondence_address = db.Column(db.Text)
    scopus_author_id = db.Column(db.String(255))
    orcid_id = db.Column(db.String(255))
    google_scholar_id_link = db.Column(db.String(255))
    aicte_id = db.Column(db.String(255))
    scet_id = db.Column(db.String(255))
    visibility = db.Column(db.Enum(Visibility.SHOW, Visibility.HIDE), default=Visibility.SHOW)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FacultyAdditionalDetails {self.detail_id}>'


class WorkExperience(db.Model):
    """Work experience model for faculty."""
    __tablename__ = 'work_experiences'
    
    experience_id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=False)
    institution_name = db.Column(db.String(255), nullable=False)
    experience_type = db.Column(db.Enum(ExperienceTypes.TEACHING, ExperienceTypes.INDUSTRY), nullable=False)
    designation = db.Column(db.String(255))
    from_date = db.Column(db.Date)
    to_date = db.Column(db.Date)
    number_of_years = db.Column(db.Integer)
    responsibilities = db.Column(db.Text)
    service_certificate_attachment_id = db.Column(db.Integer, db.ForeignKey('attachments.attachment_id'))
    visibility = db.Column(db.Enum(Visibility.SHOW, Visibility.HIDE), default=Visibility.SHOW)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_certificate = db.relationship('Attachment', foreign_keys=[service_certificate_attachment_id])
    
    def __repr__(self):
        return f'<WorkExperience {self.institution_name}>'


class TeachingActivity(db.Model):
    """Teaching activities model for faculty."""
    __tablename__ = 'teaching_activities'
    
    activity_id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    semester = db.Column(db.String(20))
    year = db.Column(db.Integer)
    course_code = db.Column(db.String(20))
    description = db.Column(db.Text)
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachments.attachment_id'))
    visibility = db.Column(db.Enum(Visibility.SHOW, Visibility.HIDE), default=Visibility.SHOW)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attachment = db.relationship('Attachment', foreign_keys=[attachment_id])
    
    def __repr__(self):
        return f'<TeachingActivity {self.course_name}>'


class ResearchPublication(db.Model):
    """Research publications model for faculty."""
    __tablename__ = 'research_publications'
    
    publication_id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    journal_name = db.Column(db.String(200))
    type_id = db.Column(db.Integer, db.ForeignKey('lookup_tables.lookup_id'))
    publication_date = db.Column(db.Date)
    doi = db.Column(db.String(50))
    description = db.Column(db.Text)
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachments.attachment_id'))
    visibility = db.Column(db.Enum(Visibility.SHOW, Visibility.HIDE), default=Visibility.SHOW)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    type = db.relationship('LookupTable', foreign_keys=[type_id])
    attachment = db.relationship('Attachment', foreign_keys=[attachment_id])
    
    def __repr__(self):
        return f'<ResearchPublication {self.title}>'


class WorkshopSeminar(db.Model):
    """Workshops and seminars model for faculty."""
    __tablename__ = 'workshops_seminars'
    
    workshop_id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('lookup_tables.lookup_id'))
    location = db.Column(db.String(100))
    organized_by = db.Column(db.String(200))
    date = db.Column(db.Date)
    description = db.Column(db.Text)
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachments.attachment_id'))
    visibility = db.Column(db.Enum(Visibility.SHOW, Visibility.HIDE), default=Visibility.SHOW)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    type = db.relationship('LookupTable', foreign_keys=[type_id])
    attachment = db.relationship('Attachment', foreign_keys=[attachment_id])
    
    def __repr__(self):
        return f'<WorkshopSeminar {self.title}>'


class MDPFDP(db.Model):
    """MDP/FDP model for faculty."""
    __tablename__ = 'mdp_fdp'
    
    fdp_id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('lookup_tables.lookup_id'))
    location = db.Column(db.String(100))
    organized_by = db.Column(db.String(200))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachments.attachment_id'))
    visibility = db.Column(db.Enum(Visibility.SHOW, Visibility.HIDE), default=Visibility.SHOW)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    type = db.relationship('LookupTable', foreign_keys=[type_id])
    attachment = db.relationship('Attachment', foreign_keys=[attachment_id])
    
    def __repr__(self):
        return f'<MDPFDP {self.title}>'


class HonoursAward(db.Model):
    """Honours and awards model for faculty."""
    __tablename__ = 'honours_awards'
    
    award_id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=False)
    award_title = db.Column(db.String(200), nullable=False)
    awarded_by = db.Column(db.String(200))
    date = db.Column(db.Date)
    category_id = db.Column(db.Integer, db.ForeignKey('lookup_tables.lookup_id'))
    description = db.Column(db.Text)
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachments.attachment_id'))
    visibility = db.Column(db.Enum(Visibility.SHOW, Visibility.HIDE), default=Visibility.SHOW)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('LookupTable', foreign_keys=[category_id])
    attachment = db.relationship('Attachment', foreign_keys=[attachment_id])
    
    def __repr__(self):
        return f'<HonoursAward {self.award_title}>'

class ResearchConsultancy(db.Model):
    """Research and consultancy projects model for faculty."""
    __tablename__ = 'research_consultancy'
    
    project_id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=False)
    project_title = db.Column(db.String(200), nullable=False)
    agency_id = db.Column(db.Integer, db.ForeignKey('lookup_tables.lookup_id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.Enum('Ongoing', 'Completed'))
    description = db.Column(db.Text)
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachments.attachment_id'))
    visibility = db.Column(db.Enum(Visibility.SHOW, Visibility.HIDE), default=Visibility.SHOW)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agency = db.relationship('LookupTable', foreign_keys=[agency_id])
    attachment = db.relationship('Attachment', foreign_keys=[attachment_id])
    
    def __repr__(self):
        return f'<ResearchConsultancy {self.project_title}>'


class Activity(db.Model):
    """Other activities model for faculty."""
    __tablename__ = 'activities'
    
    activity_id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=False)
    activity_title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(100))
    date = db.Column(db.Date)
    description = db.Column(db.Text)
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachments.attachment_id'))
    visibility = db.Column(db.Enum(Visibility.SHOW, Visibility.HIDE), default=Visibility.SHOW)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attachment = db.relationship('Attachment', foreign_keys=[attachment_id])
    
    def __repr__(self):
        return f'<Activity {self.activity_title}>'


class LookupTable(db.Model):
    """Lookup tables for normalized data."""
    __tablename__ = 'lookup_tables'
    
    lookup_id = db.Column(db.Integer, primary_key=True)
    lookup_type = db.Column(db.String(50), nullable=False)
    lookup_value = db.Column(db.String(100), nullable=False, unique=True)
    
    def __repr__(self):
        return f'<LookupTable {self.lookup_type}: {self.lookup_value}>'