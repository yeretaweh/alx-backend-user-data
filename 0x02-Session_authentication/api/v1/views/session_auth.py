#!/usr/bin/env python3
""" View for Session Authentication
"""
from flask import jsonify, request, abort
from models.user import User
from api.v1.views import app_views
from os import getenv


@app_views.route('/auth_session/login', methods=[
    'POST'], strict_slashes=False)
def login():
    """ POST /auth_session/login
    Handles user login using session authentication
    """
    # Retrieve email and password from form data
    email = request.form.get('email')
    password = request.form.get('password')

    # Check if email is provided
    if not email or email == "":
        return jsonify({"error": "email missing"}), 400

    # Check if password is provided
    if not password or password == "":
        return jsonify({"error": "password missing"}), 400

    # Search for the user by email
    users = User.search({"email": email})
    if not users or len(users) == 0:
        return jsonify({"error": "no user found for this email"}), 404

    user = users[0]  # Assuming email is unique, take the first user

    # Check if the password is valid
    if not user.is_valid_password(password):
        return jsonify({"error": "wrong password"}), 401

    # Import auth to create session (avoid circular import issues)
    from api.v1.app import auth

    # Create a session for the user
    session_id = auth.create_session(user.id)

    # Create response with user info
    response = jsonify(user.to_json())

    # Set session cookie in the response
    session_name = getenv("SESSION_NAME")
    response.set_cookie(session_name, session_id)

    return response


@app_views.route('auth_session/logout', methods=[
    'DELETE'], strict_slashes=False)
def logout():
    """ DELETE /auth_session/logout
    Handles user logout by deleting the session
    """
    from api.v1.app import auth

    # Destroy session using auth.destroy_session
    if auth.destroy_session(request):
        return jsonify({}), 200
    else:
        abort(404)
