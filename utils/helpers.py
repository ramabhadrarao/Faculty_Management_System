import os
import uuid
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def generate_unique_filename(filename):
    """Generate a unique filename to prevent collisions."""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    unique_id = uuid.uuid4().hex
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{timestamp}_{unique_id}.{ext}" if ext else f"{timestamp}_{unique_id}"

def get_file_path(filename, subfolder=None):
    """Get the full path to save a file."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    if subfolder:
        full_path = os.path.join(upload_folder, subfolder)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
    else:
        full_path = upload_folder
        
    return os.path.join(full_path, filename)

def save_file(file_obj, subfolder=None):
    """Save a file and return the path."""
    filename = secure_filename(file_obj.filename)
    unique_filename = generate_unique_filename(filename)
    file_path = get_file_path(unique_filename, subfolder)
    file_obj.save(file_path)
    
    # Return the relative path
    return os.path.join(subfolder, unique_filename) if subfolder else unique_filename

def delete_file(file_path):
    """Delete a file from storage."""
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_path)
    if os.path.exists(full_path):
        os.remove(full_path)
        return True
    return False

def format_date(date_obj, format_str='%Y-%m-%d'):
    """Format a date object as string."""
    if not date_obj:
        return None
    return date_obj.strftime(format_str)

def parse_date(date_str, format_str='%Y-%m-%d'):
    """Parse a date string into a date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None

def calculate_years_of_experience(from_date, to_date):
    """Calculate years of experience between two dates."""
    if not from_date or not to_date:
        return None
    
    delta = to_date - from_date
    years = delta.days // 365
    return years
