#!/usr/bin/env python3
"""This module handles basic authentication for the API"""

from flask import request
from typing import List, TypeVar
import os


class Auth:
    """Template which handles authentication for the API"""

    def require_auth(self, path: str, excluded_paths: list) -> bool:
        """
        Determines if a given path requires authentication.

        Args:
            path (str): The path to check.
            excluded_paths (list): A list of paths that are excluded from
                                authentication, which can include
                                wildcards (*).

        Returns:
            bool: True if authentication is required,
            False if the path is excluded.
        """
        if path is None or excluded_paths is None or len(excluded_paths) == 0:
            return True

        # Normalize the path (ensure it has no trailing slash)
        if path[-1] != '/':
            path += '/'

        for excluded_path in excluded_paths:
            # Check if excluded_path ends with '*' (wildcard)
            if excluded_path.endswith('*'):
                # Remove the '*' and compare with
                # the start of the requested path
                if path.startswith(excluded_path[:-1]):
                    return False
            else:
                # If exact match, return False (no authentication required)
                if path == excluded_path:
                    return False

        return True

    def authorization_header(self, request=None) -> str:
        """Retrieves the authorization header from a request.
        If no Authorization header is present, returns None.
        """
        if request is None:
            return None
        return request.headers.get('Authorization', None)

    def current_user(self, request=None) -> TypeVar('User'):
        """Retrieves the current user from a request."""
        return None

    def session_cookie(self, request=None):
        """Returns the session cookie value from a request

        Args:
            request (Flask request object): The Flask request object.

        Returns:
            str: The session cookie value or None.
        """
        if request is None:
            return None

        # Retrieve the session cookie name from the environment variable
        session_cookie_name = os.getenv('SESSION_NAME')
        if session_cookie_name is None:
            return None

        # Retrieve the session cookie value from the request
        return request.cookies.get(session_cookie_name)
