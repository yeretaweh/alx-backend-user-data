#!/usr/bin/env python3
"""Auth module that handles authentication related tasks
"""

import bcrypt
from db import DB
from user import User
from sqlalchemy.orm.exc import NoResultFound
from uuid import uuid4
from typing import Union


def _hash_password(password: str) -> bytes:
    """Hashes a password using bcrypt's hashing algo and
    returns hashed password as bytes.

    Args:
        password (str): The password to hash.

    Returns:
        bytes: The hashed password.
    """
    salt: bytes = bcrypt.gensalt()  # Generate a salt
    hashed_password: bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


def _generate_uuid() -> str:
    """Generates a new uuid and returns it as a string."""
    return str(uuid4())


class Auth:
    """Auth class to interact with the authentication database."""

    def __init__(self):
        """Initialize the Auth instance with a database instance."""
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """
        Registers a user with the given email and password.

        Args:
            email (str): The user's email.
            password (str): The user's password.

        Returns:
            User: The newly created User object.

        Raises:
            ValueError: If the user already exists with the given email.
        """
        try:
            existing_user = self._db.find_user_by(email=email)
            if existing_user:
                raise ValueError(f"User {email} already exists")
        except NoResultFound:
            hashed_password = _hash_password(password)
            new_user = self._db.add_user(
                email, hashed_password.decode('utf-8'))
            return new_user

    def valid_login(self, email: str, password: str) -> bool:
        """Check if login credentials are valid.

        Args:
            email (str): The user's email.
            password (str): The user's password.

        Returns:
            bool: True if valid login, else False.
        """
        try:
            # Find user by email
            user = self._db.find_user_by(email=email)

            # Check if the provided password matches the stored hashed password
            if bcrypt.checkpw(password.encode(
                    'utf-8'), user.hashed_password.encode('utf-8')):
                return True
            return False
        except NoResultFound:
            # Return False if no user is found with the provided email
            return False

    def create_session(self, email: str) -> str:
        """Generate session ID for a user and return it.

        Args:
            email (str): The user's email.

        Returns:
            str: The session ID or None if the user is not found.
        """
        try:
            user = self._db.find_user_by(email=email)
            session_id = _generate_uuid()
            self._db.update_user(user.id, session_id=session_id)
            return session_id
        except NoResultFound:
            return None

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        """Returns the User associated with the given session ID.

        Args:
            session_id (str): The session ID to query.

        Returns:
            User | None: User object if found, else None.
        """
        if session_id is None:
            return None
        try:
            # Query the db for a user with the given session_id
            user = self._db.find_user_by(session_id=session_id)
            return user
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        """Destroys a session by setting the session_id to None
        for the given user.

        Args:
            user_id (int): The user's ID whose session should be destroyed.

        Returns:
            None
        """
        try:
            # Find the user by user_id
            user = self._db.find_user_by(id=user_id)

            # Set the user's session_id to None
            self._db.update_user(user.id, session_id=None)

        except NoResultFound:
            # If no user is found, just return None
            return None

    def get_reset_password_token(self, email: str) -> str:
        """Generate a password reset token for a user.

        Args:
            email (str): The user's email.

        Returns:
            str: The password reset token or None if the user is not found.

        Raises:
            ValueError: If the user does not exist with the given email.
        """
        try:
            # Find the user by email
            user = self._db.find_user_by(email=email)

            # Generate a new UUID for the reset token
            reset_token = _generate_uuid()

            # Update the user with the reset token
            self._db.update_user(user.id, reset_token=reset_token)

            # Return the generated token
            return reset_token
        except NoResultFound:
            # Raise ValueError if no user is found with the given email
            raise ValueError

    def update_password(self, reset_token: str, password: str) -> None:
        """Updates a user's password using the reset_token.

        Args:
            reset_token (str): The reset token provided by the user.
            password (str): The new password to be updated.

        Raises:
            ValueError: If no user is found with the given reset_token.
        """
        try:
            # Find user by reset_token
            user = self._db.find_user_by(reset_token=reset_token)

            # Hash the new password
            hashed_password = _hash_password(password).decode('utf-8')

            # Update the user's password and claer the reset_token
            self._db.update_user(
                user.id, hashed_password=hashed_password, reset_token=None)

        except NoResultFound:
            # Raise ValueError if no user is found with the given reset_token
            raise ValueError
