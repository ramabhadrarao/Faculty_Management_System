from flask import current_app
from flask_principal import Principal, Permission, RoleNeed, identity_loaded
from models.user import User
from config.constants import UserRoles


# Initialize Principal with app
def setup_rbac(app):
    principal = Principal(app)
    
    # Define roles permissions
    admin_permission = Permission(RoleNeed(UserRoles.ADMIN))
    principal_permission = Permission(RoleNeed(UserRoles.PRINCIPAL))
    hod_permission = Permission(RoleNeed(UserRoles.HOD))
    faculty_permission = Permission(RoleNeed(UserRoles.FACULTY))
    
    # Register permissions with the app
    app.admin_permission = admin_permission
    app.principal_permission = principal_permission
    app.hod_permission = hod_permission
    app.faculty_permission = faculty_permission
    
    # Identity loading
    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        # Set the identity user
        if hasattr(identity, 'user'):
            user = identity.user
            
            # Add the UserNeed to the identity
            identity.provides.add(UserNeed(user.user_id))
            
            # Add each role to the identity
            for role in user.roles:
                identity.provides.add(RoleNeed(role.name))
                
                # Add each permission to the identity
                for permission in role.permissions:
                    identity.provides.add(ActionNeed(permission.name))
