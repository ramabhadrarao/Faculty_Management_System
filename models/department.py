from datetime import datetime
from models.base import db


class College(db.Model):
    """College model."""
    __tablename__ = 'college'
    
    college_id = db.Column(db.Integer, primary_key=True)
    college_name = db.Column(db.String(255), nullable=False)
    college_code = db.Column(db.String(50), unique=True, nullable=False)
    logo = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    departments = db.relationship('Department', backref='college', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<College {self.college_name}>'


class Department(db.Model):
    """Department model."""
    __tablename__ = 'departments'
    
    department_id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(255), nullable=False)
    department_code = db.Column(db.String(50), unique=True, nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('college.college_id'))
    logo = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    programs = db.relationship('Program', backref='department', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Department {self.department_name}>'

class Regulation(db.Model):
    """Regulation model."""
    __tablename__ = 'regulations'
    
    regulation_id = db.Column(db.Integer, primary_key=True)
    regulation_name = db.Column(db.String(255), nullable=False)
    regulation_code = db.Column(db.String(50), unique=True, nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.program_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Regulation {self.regulation_name}>'
        
class Program(db.Model):
    """Program model."""
    __tablename__ = 'programs'
    
    program_id = db.Column(db.Integer, primary_key=True)
    program_name = db.Column(db.String(255), nullable=False)
    program_code = db.Column(db.String(50), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    branches = db.relationship('Branch', backref='program', cascade='all, delete-orphan')
    regulations = db.relationship('Regulation', backref='program', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Program {self.program_name}>'


class Branch(db.Model):
    """Branch model."""
    __tablename__ = 'branches'
    
    branch_id = db.Column(db.Integer, primary_key=True)
    branch_name = db.Column(db.String(255), nullable=False)
    branch_code = db.Column(db.String(50), unique=True, nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.program_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Branch {self.branch_name}>'