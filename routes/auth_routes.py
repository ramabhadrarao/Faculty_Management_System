from flask import Blueprint, request, redirect, url_for
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return AuthController.register(request)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return AuthController.login(request)

@auth_bp.route('/logout')
def logout():
    return AuthController.logout()

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    return AuthController.forgot_password(request)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    return AuthController.reset_password(request, token)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    return AuthController.change_password(request)