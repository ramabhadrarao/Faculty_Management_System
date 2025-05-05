# Faculty Management System

A comprehensive full-stack application for managing faculty information, profiles, and academic activities with role-based access control.

## Features

### User Management
- Multi-role system (Admin, Principal, HOD, Faculty)
- Secure authentication with password hashing
- Role-based access control
- JWT token authentication for API endpoints

### Faculty Profile Management
- Faculty self-registration and profile creation
- Comprehensive faculty profile with personal and professional details
- Upload and manage documents (Aadhar, PAN, photo, certificates)
- Profile freeze/unfreeze mechanism
- Approval workflow by HOD/Admin

### Academic Activities Tracking
- Work experience management
- Teaching activities
- Research publications
- Workshops and seminars attendance
- FDP/MDP participation records
- Honours and awards
- Research and consultancy projects

### Department Management
- Department hierarchy (College > Department > Program > Branch)
- Department-wise faculty view
- HOD assignment

### Reports and Analytics
- Department-wise faculty reports
- Status-based faculty reports (pending, approved, frozen)
- Faculty statistics and metrics

### Rest API
- Complete REST API for mobile app integration
- JWT authentication for API endpoints
- CRUD operations for all major functionalities

## Technology Stack

### Backend
- Python 3.9+
- Flask web framework
- Flask extensions:
  - Flask-SQLAlchemy (ORM)
  - Flask-Login (Session-based authentication)
  - Flask-JWT-Extended (API authentication)
  - Flask-Principal (RBAC)
  - Flask-Mail (Email notifications)
  - Flask-WTF (Form validation and CSRF protection)
  - Flask-Cors (CORS support for API)

### Database
- MySQL (with SQLAlchemy ORM)

### Frontend
- Tabler UI (Dashboard template)
- HTML/CSS/JavaScript
- Bootstrap 5

## Project Structure

```
faculty_management_system/
│
├── app.py                      # Application entry point
├── config/                     # Configuration settings
│   ├── __init__.py
│   ├── config.py               # Environment-specific configuration
│   └── constants.py            # Application constants
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── security.py             # Security-related utilities
│   ├── helpers.py              # Generic helper functions
│   └── validators.py           # Input validation
│
├── email/                      # Email functionality
│   ├── __init__.py
│   ├── templates/              # Email templates
│   └── email_service.py        # Email sending service
│
├── models/                     # Database models
│   ├── __init__.py
│   ├── base.py                 # Base DB setup
│   ├── user.py                 # User and role models
│   ├── faculty.py              # Faculty-related models
│   ├── department.py           # Department hierarchy models
│   └── attachment.py           # File attachment models
│
├── controllers/                # Business logic
│   ├── __init__.py
│   ├── auth_controller.py      # Authentication logic
│   ├── faculty_controller.py   # Faculty management
│   ├── admin_controller.py     # Admin functionality
│   ├── hod_controller.py       # HOD functionality
│   └── file_controller.py      # File upload/download
│
├── routes/                     # Route definitions
│   ├── __init__.py
│   ├── auth_routes.py          # Authentication routes
│   ├── faculty_routes.py       # Faculty routes
│   ├── admin_routes.py         # Admin routes
│   ├── hod_routes.py           # HOD routes
│   └── api/                    # API routes
│       ├── __init__.py
│       ├── auth_api.py         # Auth API
│       ├── faculty_api.py      # Faculty API
│       └── admin_api.py        # Admin API
│
├── middleware/                 # Middleware components
│   ├── __init__.py
│   ├── auth_middleware.py      # Authentication middleware
│   └── rbac_middleware.py      # Role-based access control
│
├── static/                     # Static assets
│   ├── css/
│   ├── js/
│   ├── images/
│   └── uploads/                # Uploaded files
│
└── templates/                  # HTML templates
    ├── base.html               # Base template
    ├── auth/                   # Authentication templates
    ├── faculty/                # Faculty dashboard templates
    ├── hod/                    # HOD dashboard templates
    └── admin/                  # Admin dashboard templates
```

## Database Schema

The system uses a comprehensive database schema with the following key tables:

1. **User-related tables**:
   - users
   - roles
   - user_roles
   - permissions
   - role_permissions

2. **Faculty-related tables**:
   - faculty
   - faculty_additional_details
   - work_experiences
   - teaching_activities
   - research_publications
   - workshops_seminars
   - mdp_fdp
   - honours_awards
   - research_consultancy
   - activities

3. **Department-related tables**:
   - college
   - departments
   - programs
   - branches

4. **File-related tables**:
   - attachments

## Setup Instructions

### Prerequisites
- Python 3.9 or higher
- MySQL 5.7 or higher
- pip (Python package installer)
- virtualenv (optional but recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/faculty-management-system.git
cd faculty-management-system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (or create a .env file):
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URL=mysql+pymysql://username:password@localhost/faculty_management
JWT_SECRET_KEY=your_jwt_secret_key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_password
MAIL_USE_TLS=True
MAIL_DEFAULT_SENDER=your_email@gmail.com
```

5. Initialize the database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. Run the application:
```bash
flask run
```

7. Access the application at `http://localhost:5000`

### Initial Login
- Username: admin
- Password: admin123
- *Change this password immediately after first login*

## API Documentation

The system provides a comprehensive REST API for mobile app integration. All API endpoints are prefixed with `/api`.

### Authentication Endpoints

- `POST /api/auth/login` - User login (returns JWT token)
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/register` - User registration

### Faculty Endpoints

- `GET /api/faculty/profile` - Get current faculty profile
- `POST /api/faculty/profile` - Create new faculty profile
- `PUT /api/faculty/profile/<faculty_id>` - Update faculty profile
- `PUT /api/faculty/additional-details/<faculty_id>` - Update additional details
- `GET /api/faculty/work-experience/<faculty_id>` - Get work experiences
- `POST /api/faculty/work-experience/<faculty_id>` - Add work experience
- `DELETE /api/faculty/work-experience/<faculty_id>/<experience_id>` - Delete work experience
- `POST /api/faculty/freeze/<faculty_id>` - Freeze faculty profile

### Admin Endpoints

- `GET /api/admin/dashboard-stats` - Get admin dashboard statistics
- `GET /api/admin/users` - Get all users
- `GET /api/admin/departments` - Get all departments
- `GET /api/admin/pending-approvals` - Get faculty profiles pending approval
- `POST /api/admin/approve-profile/<faculty_id>` - Approve faculty profile
- `POST /api/admin/unfreeze-profile/<faculty_id>` - Unfreeze faculty profile

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

- Your Name <your.email@example.com>

## Acknowledgments

- Thanks to all the open-source libraries used in this project
- Tabler UI for the beautiful dashboard template
