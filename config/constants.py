# User roles
class UserRoles:
    ADMIN = 'admin'
    PRINCIPAL = 'principal'
    HOD = 'hod'
    FACULTY = 'faculty'
    STUDENT = 'student'

# Faculty profile status
class ProfileStatus:
    PENDING = 'pending'
    APPROVED = 'approved'
    FROZEN = 'frozen'
    UNFROZEN = 'unfrozen'

# Visibility options
class Visibility:
    SHOW = 'show'
    HIDE = 'hide'

# Work experience types
class ExperienceTypes:
    TEACHING = 'Teaching'
    INDUSTRY = 'Industry'

# Publication types (for lookup_tables)
PUBLICATION_TYPES = [
    'Journal', 
    'Conference', 
    'Book Chapter', 
    'Book', 
    'Patent'
]

# Workshop types (for lookup_tables)
WORKSHOP_TYPES = [
    'Attended',
    'Organized',
    'Conducted'
]

# FDP/MDP types (for lookup_tables)
FDP_MDP_TYPES = [
    'Faculty Development Program',
    'Management Development Program',
    'Staff Development Program',
    'Training Program'
]

# Award categories (for lookup_tables)
AWARD_CATEGORIES = [
    'Teaching Excellence',
    'Research',
    'Innovation',
    'Service',
    'Leadership',
    'Lifetime Achievement'
]