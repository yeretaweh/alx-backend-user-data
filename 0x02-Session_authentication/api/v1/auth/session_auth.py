#!/usr/bin/env python3
""" This module handles session authentication for the API """
from api.v1.auth.auth import Auth
from uuid import uuid4
from models.user import User


class SessionAuth(Auth):
    """ This class handles session authentication for the API """

    # Class attribute to store session IDs and corresponding user IDs
    user_id_by_session_id = {}

    def create_session(self, user_id: str = None) -> str:
        """Creates a session ID for a given user ID and stores it

        Args:
            user_id (str): The ID of the user for whom
            the session is created.

        Returns:
            str: The session ID generated, or None if input is invalid.
        """
        if user_id is None or not isinstance(user_id, str):
            return None

        # Generate a session ID using uuid4
        session_id = str(uuid4())

        # Store the session ID with the user ID in the dictionary
        self.user_id_by_session_id[session_id] = user_id

        return session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """Retrieves the user ID associated with a given session ID

        Args:
            session_id (str): The session ID to retrieve the user ID for.

        Returns:
            str: The user ID associated with the session ID, or None
            if the session ID is invalid or not found.
        """
        if session_id is None or not isinstance(session_id, str):
            return None

        return self.user_id_by_session_id.get(session_id)

    def current_user(self, request=None) -> str:
        """Returns a User instance based on a cookie value"""

        # Get session ID from cookie
        session_id = self.session_cookie(request)

        if session_id is None:
            return None

        # Get user ID based on the session ID
        user_id = self.user_id_for_session_id(session_id)

        if user_id is None:
            return None

        return User.get(user_id)  # Get User instance based on user ID

    def destroy_session(self, request=None):
        """ Deletes the user session (logout) """
        if request is None:
            return False

        # Get the session cookie from the request
        session_id = self.session_cookie(request)
        if session_id is None:
            return False

        # Retrieve user ID from session ID
        user_id = self.user_id_for_session_id(session_id)
        if user_id is None:
            return False

        # Remove the session ID from the session dictionary
        if session_id in self.user_id_by_session_id:
            del self.user_id_by_session_id[session_id]
            return True

        return False
