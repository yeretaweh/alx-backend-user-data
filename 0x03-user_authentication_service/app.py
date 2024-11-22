#!/usr/bin/env python3
"""Flask app module that handles the app initialization."""

from flask import (
    Flask,
    jsonify,
    request,
    abort,
    make_response,
    url_for,
    redirect
)
from auth import Auth


app = Flask(__name__)

# Instantiate the Auth object
AUTH = Auth()


@app.route('/', methods=['GET'])
def welcome() -> str:
    """Return a welcome message."""
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=['POST'])
def register_user() -> str:
    """POST /users route handler that registers a new user."""

    email = request.form.get('email')
    password = request.form.get('password')

    try:
        # Register the user using Auth
        user = AUTH.register_user(email, password)
        return jsonify({"email": user.email, "message": "user created"}), 200
    except ValueError:
        # If the user already exists, return error message
        return jsonify({"message": "email already registered"}), 400


@app.route("/sessions", methods=['POST'])
def login():
    """POST /sessions route handler that logs in a user."""
    # Get the email and password from the form data
    email = request.form.get('email')
    password = request.form.get('password')

    # Validate the credentials
    if not AUTH.valid_login(email, password):
        abort(401)

    # Create a session ID for the user
    session_id = AUTH.create_session(email)

    # If session ID is generated, set the session cookie and return response
    if session_id:
        res = make_response(jsonify({"email": email, "message": "logged in"}))

        # Set the session_id in the response cookie
        res.set_cookie("session_id", session_id)

        return res

    # If something goes wrong, abort with an error
    abort(401)


@app.route("/sessions", methods=['DELETE'])
def logout():
    """DELETE /sessions route handler that logs out a user."""

    # Retrieve the session ID from cookies
    session_id = request.cookies.get("session_id")

    if session_id is None:
        # If no session ID is found, abort with 403 error
        abort(403)

    # Get the user corresponding to the session ID
    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        abort(403)

    # Destroy the session for the user
    AUTH.destroy_session(user.id)

    # Redirect to the home page
    return redirect(url_for("welcome"))


@app.route("/profile", methods=['GET'])
def profile() -> str:
    """GET /profile route handler that returns a user's profile."""

    # Retrieve the session ID from cookies
    session_id = request.cookies.get("session_id")

    if session_id is None:
        # If no session_id cookie is found, resoond with 403 error
        abort(403)

    # Get the user corresponding to the session ID
    user = AUTH.get_user_from_session_id(session_id)

    if user is None:
        # If no user is found, respond with 403 error
        abort(403)

    # Respond with the user's email and 200 status code
    return jsonify({"email": user.email}), 200


@app.route("/reset_password", methods=['POST'])
def reset_password() -> str:
    """POST /reset_password route handler to generate reset password token"""
    email = request.form.get('email')

    try:
        # Generate reset password token using AUTH
        reset_token = AUTH.get_reset_password_token(email)

        # Respond with user's email and reset token
        return jsonify({"email": email, "reset_token": reset_token}), 200

    except ValueError:
        # If user is not found, respond with 403 error
        abort(403)


@app.route("/reset_password", methods=['PUT'])
def update_password() -> str:
    """PUT /reset_password route handler to update user's password"""
    email = request.form.get('email')
    reset_token = request.form.get('reset_token')
    new_password = request.form.get('new_password')

    # Validate input
    if not email or not reset_token or not new_password:
        abort(400)

    try:
        # Update the user's password
        AUTH.update_password(reset_token, new_password)

        return jsonify({"email": email, "message": "Password updated"}), 200

    except ValueError:
        # If user is not found, respond with 403 error
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
