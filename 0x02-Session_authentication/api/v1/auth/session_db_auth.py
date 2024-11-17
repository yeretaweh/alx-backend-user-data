#!/usr/bin/env python3
"""Module that provides functionality to manage sessions stored in DB"""
from api.v1.auth.session_exp_auth import SessionExpAuth
from models.user_session import UserSession
from datetime import datetime, timedelta


class SessionDBAuth(SessionExpAuth):
    """SessionDBAuth class for managing sessions stored in database"""

    def create_session(self, user_id=None):
        """Creates a session and stores it in the database"""
        session_id = super().create_session(user_id)
        if not session_id:
            return None

        # Create a new UserSession instance and save it
        user_session = UserSession(user_id=user_id, session_id=session_id)
        user_session.save()

        return session_id

    def user_id_for_session_id(self, session_id=None):
        """Returns the user ID associated with
        the session from the database
        """
        if session_id is None:
            return None

        # Load UserSession from the database
        try:
            all_sessions = UserSession.all()
            for session in all_sessions:
                if session.session_id == session_id:
                    # Check if the session has expired
                    if self.session_duration <= 0:
                        return session.user_id
                    created_at = session.created_at
                    if created_at + timedelta(
                            seconds=self.session_duration) < datetime.now():
                        return None
                    return session.user_id
        except (FileNotFoundError, KeyError):
            return None

        return None

    def destroy_session(self, request=None):
        """Destroys a session based on the session ID"""
        if request is None:
            return False

        session_id = self.session_cookie(request)
        if not session_id:
            return False

        try:
            all_sessions = UserSession.all()
            # Filter out the session to delete
            new_sessions = [
                session for session in all_sessions
                if session.session_id != session_id]

            if len(new_sessions) == len(all_sessions):  # No session found
                return False

            # Save updated sessions to the file
            UserSession.save_to_file(new_sessions)
            return True
        except (FileNotFoundError, KeyError):
            return False
