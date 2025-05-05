from flask import current_app, render_template
from flask_mail import Message, Mail
from threading import Thread

def send_async_email(app, mail, msg):
    """Send email asynchronously."""
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, text_body, html_body=None, sender=None, attachments=None):
    """Send an email."""
    app = current_app._get_current_object()
    mail = Mail(app)
    
    msg = Message(subject, recipients=recipients, sender=sender or app.config['MAIL_DEFAULT_SENDER'])
    msg.body = text_body
    
    if html_body:
        msg.html = html_body
    
    if attachments:
        for attachment in attachments:
            msg.attach(attachment['filename'], attachment['mimetype'], attachment['data'])
    
    # Send email asynchronously to not block the request
    Thread(target=send_async_email, args=(app, mail, msg)).start()

def send_password_reset_email(user_email, token):
    """Send password reset email."""
    app = current_app._get_current_object()
    reset_url = f"{app.config.get('APP_URL', 'http://localhost:5000')}/auth/reset-password/{token}"
    
    subject = "Password Reset Request"
    
    text_body = f"""
    To reset your password, visit the following link:
    {reset_url}
    
    If you did not make this request, please ignore this email.
    
    The link will expire in 24 hours.
    """
    
    html_body = render_template('email/reset_password.html', reset_url=reset_url)
    
    send_email(subject, [user_email], text_body, html_body)

def send_account_activation_email(user_email, token):
    """Send account activation email."""
    app = current_app._get_current_object()
    activation_url = f"{app.config.get('APP_URL', 'http://localhost:5000')}/auth/activate/{token}"
    
    subject = "Account Activation"
    
    text_body = f"""
    To activate your account, visit the following link:
    {activation_url}
    
    If you did not create an account, please ignore this email.
    
    The link will expire in 24 hours.
    """
    
    html_body = render_template('email/activate_account.html', activation_url=activation_url)
    
    send_email(subject, [user_email], text_body, html_body)

def send_profile_approval_notification(faculty):
    """Send notification email when a faculty profile is approved."""
    subject = "Faculty Profile Approved"
    
    text_body = f"""
    Dear {faculty.full_name},
    
    Your faculty profile has been approved. You can now log in to the Faculty Management System to access all features.
    
    Thank you.
    """
    
    html_body = render_template('email/profile_approved.html', faculty=faculty)
    
    send_email(subject, [faculty.email], text_body, html_body)

def send_profile_freeze_notification(faculty):
    """Send notification email when a faculty profile is frozen."""
    subject = "Faculty Profile Frozen"
    
    text_body = f"""
    Dear {faculty.full_name},
    
    Your faculty profile has been frozen. This means it can no longer be edited until unfrozen by an administrator or HOD.
    
    Thank you.
    """
    
    html_body = render_template('email/profile_frozen.html', faculty=faculty)
    
    send_email(subject, [faculty.email], text_body, html_body)

def send_profile_unfreeze_notification(faculty):
    """Send notification email when a faculty profile is unfrozen."""
    subject = "Faculty Profile Unfrozen"
    
    text_body = f"""
    Dear {faculty.full_name},
    
    Your faculty profile has been unfrozen. You can now edit your profile information.
    
    Thank you.
    """
    
    html_body = render_template('email/profile_unfrozen.html', faculty=faculty)
    
    send_email(subject, [faculty.email], text_body, html_body)