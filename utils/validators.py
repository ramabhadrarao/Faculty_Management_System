import re
from datetime import datetime

def validate_email(email):
    """Validate email format."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+
    return bool(re.match(pattern, email))

def validate_password(password):
    """
    Validate password strength.
    - At least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    """
    if len(password) < 8:
        return False
    
    if not re.search(r'[A-Z]', password):
        return False
    
    if not re.search(r'[a-z]', password):
        return False
    
    if not re.search(r'\d', password):
        return False
    
    return True

def validate_phone_number(phone_number):
    """Validate phone number format."""
    pattern = r'^\+?[0-9]{10,15}
    return bool(re.match(pattern, phone_number))

def validate_aadhar_number(aadhar_number):
    """Validate Aadhar number (12 digits)."""
    pattern = r'^[0-9]{12}
    return bool(re.match(pattern, aadhar_number))

def validate_pan_number(pan_number):
    """Validate PAN number (10 alphanumeric characters)."""
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}
    return bool(re.match(pattern, pan_number))

def validate_date_range(start_date, end_date):
    """Validate that start date is before end date."""
    if not start_date or not end_date:
        return True
    
    return start_date < end_date

def validate_date_not_future(date_obj):
    """Validate that a date is not in the future."""
    if not date_obj:
        return True
    
    return date_obj <= datetime.now().date()