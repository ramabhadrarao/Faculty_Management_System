from flask import current_app, flash, redirect, render_template, request, url_for, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models.base import db
from models.user import User, Role, UserRole
from config.constants import UserRoles
from utils.security import generate_password_reset_token, verify_reset_token
from mailservice.email_service import send_password_reset_email
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    submit = SubmitField('Register')



class AuthController:
    """Controller for authentication-related operations."""
    
    @staticmethod
    def register(request):
        """Register a new user."""
        form = RegistrationForm()
        
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = form.password.data
            first_name = form.first_name.data
            last_name = form.last_name.data
            
            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return render_template('auth/register.html', form=form)
                
            if User.query.filter_by(email=email).first():
                flash('Email already exists', 'danger')
                return render_template('auth/register.html', form=form)
                
            # Create user
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.password = password  # This will hash the password
            
            # Add faculty role by default for new registrations
            faculty_role = Role.query.filter_by(name=UserRoles.FACULTY).first()
            if faculty_role:
                user.roles.append(faculty_role)
                
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
            
        return render_template('auth/register.html', form=form)
    
    @staticmethod
    def login(request):
        """Log in a user."""
        form = LoginForm()
        
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            remember = form.remember.data
            
            # Find user by username
            user = User.query.filter_by(username=username).first()
            
            # Check if user exists and password is correct
            if not user or not user.verify_password(password):
                flash('Invalid username or password', 'danger')
                return render_template('auth/login.html', form=form)
                
            # Check if user is active
            if not user.is_active:
                flash('Your account is inactive. Contact administrator.', 'danger')
                return render_template('auth/login.html', form=form)
                
            # Log in user
            login_user(user, remember=remember)
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
                
            # Redirect based on role
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            elif user.is_principal:
                return redirect(url_for('admin.dashboard'))
            elif user.is_hod:
                return redirect(url_for('hod.dashboard'))
            else:
                return redirect(url_for('faculty.dashboard'))
                
        return render_template('auth/login.html', form=form)
    @staticmethod
    def logout():
        """Log out a user."""
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('auth.login'))
    
    @staticmethod
    def forgot_password(request):
        """Handle forgot password requests."""
        # Create a simple form for forgot password
        class ForgotPasswordForm(FlaskForm):
            email = StringField('Email', validators=[DataRequired(), Email()])
            submit = SubmitField('Send Reset Link')
            
        form = ForgotPasswordForm()
        
        if form.validate_on_submit():
            email = form.email.data
            
            user = User.query.filter_by(email=email).first()
            
            # Always show the same message to prevent email enumeration
            if user:
                token = generate_password_reset_token(user)
                send_password_reset_email(user.email, token)
                
            flash('If your email is registered, you will receive password reset instructions', 'info')
            return redirect(url_for('auth.login'))
            
        return render_template('auth/forgot_password.html', form=form)

    @staticmethod
    def reset_password(request, token):
        """Reset password using a token."""
        # Create a reset password form
        class ResetPasswordForm(FlaskForm):
            password = PasswordField('New Password', validators=[DataRequired()])
            confirm_password = PasswordField('Confirm New Password', 
                                        validators=[DataRequired(), EqualTo('password')])
            submit = SubmitField('Reset Password')
        
        form = ResetPasswordForm()
        
        # Verify token and get user
        user = verify_reset_token(token)
        
        if not user:
            flash('Invalid or expired reset token', 'danger')
            return redirect(url_for('auth.forgot_password'))
            
        if form.validate_on_submit():
            password = form.password.data
            
            # Update password
            user.password = password
            
            # Clear reset token
            user.reset_token = None
            user.reset_token_expiry = None
            
            db.session.commit()
            
            flash('Your password has been reset. You can now log in with your new password.', 'success')
            return redirect(url_for('auth.login'))
            
        return render_template('auth/reset_password.html', form=form, token=token)

    @staticmethod
    def change_password(request):
        """Change password for a logged-in user."""
        # Create a change password form
        class ChangePasswordForm(FlaskForm):
            current_password = PasswordField('Current Password', validators=[DataRequired()])
            new_password = PasswordField('New Password', validators=[DataRequired()])
            confirm_password = PasswordField('Confirm New Password', 
                                        validators=[DataRequired(), EqualTo('new_password')])
            submit = SubmitField('Change Password')
        
        form = ChangePasswordForm()
        
        if form.validate_on_submit():
            current_password = form.current_password.data
            new_password = form.new_password.data
            
            if not current_user.verify_password(current_password):
                flash('Current password is incorrect', 'danger')
                return render_template('auth/change_password.html', form=form)
                
            # Update password
            current_user.password = new_password
            db.session.commit()
            
            flash('Your password has been changed.', 'success')
            return redirect(url_for('auth.profile'))
            
        return render_template('auth/change_password.html', form=form)
    
    @staticmethod
    def forgot_password(request):
        """Handle forgot password requests."""
        # Create a simple form for forgot password
        class ForgotPasswordForm(FlaskForm):
            email = StringField('Email', validators=[DataRequired(), Email()])
            submit = SubmitField('Send Reset Link')
            
        form = ForgotPasswordForm()
        
        if form.validate_on_submit():
            email = form.email.data
            
            user = User.query.filter_by(email=email).first()
            
            # Always show the same message to prevent email enumeration
            if user:
                token = generate_password_reset_token(user)
                send_password_reset_email(user.email, token)
                
            flash('If your email is registered, you will receive password reset instructions', 'info')
            return redirect(url_for('auth.login'))
            
        return render_template('auth/forgot_password.html', form=form)

    @staticmethod
    def reset_password(request, token):
        """Reset password using a token."""
        # Create a reset password form
        class ResetPasswordForm(FlaskForm):
            password = PasswordField('New Password', validators=[DataRequired()])
            confirm_password = PasswordField('Confirm New Password', 
                                        validators=[DataRequired(), EqualTo('password')])
            submit = SubmitField('Reset Password')
        
        form = ResetPasswordForm()
        
        # Verify token and get user
        user = verify_reset_token(token)
        
        if not user:
            flash('Invalid or expired reset token', 'danger')
            return redirect(url_for('auth.forgot_password'))
            
        if form.validate_on_submit():
            password = form.password.data
            
            # Update password
            user.password = password
            
            # Clear reset token
            user.reset_token = None
            user.reset_token_expiry = None
            
            db.session.commit()
            
            flash('Your password has been reset. You can now log in with your new password.', 'success')
            return redirect(url_for('auth.login'))
            
        return render_template('auth/reset_password.html', form=form, token=token)

    @staticmethod
    def change_password(request):
        """Change password for a logged-in user."""
        # Create a change password form
        class ChangePasswordForm(FlaskForm):
            current_password = PasswordField('Current Password', validators=[DataRequired()])
            new_password = PasswordField('New Password', validators=[DataRequired()])
            confirm_password = PasswordField('Confirm New Password', 
                                        validators=[DataRequired(), EqualTo('new_password')])
            submit = SubmitField('Change Password')
        
        form = ChangePasswordForm()
        
        if form.validate_on_submit():
            current_password = form.current_password.data
            new_password = form.new_password.data
            
            if not current_user.verify_password(current_password):
                flash('Current password is incorrect', 'danger')
                return render_template('auth/change_password.html', form=form)
                
            # Update password
            current_user.password = new_password
            db.session.commit()
            
            flash('Your password has been changed.', 'success')
            return redirect(url_for('auth.profile'))
            
        return render_template('auth/change_password.html', form=form)