#!/usr/bin/env python3
"""This Module creates a persistence class to store all session IDs """

from models.base import Base


class UserSession(Base):
    """The UserSession class to store user session info"""

    def __init__(self, *args: list, **kwargs: dict):
        """ Initialize a UserSession instance
        """
        super().__init__(*args, **kwargs)
        self.user_id = kwargs.get('user_id')
        self.session_id = kwargs.get('session_id')
