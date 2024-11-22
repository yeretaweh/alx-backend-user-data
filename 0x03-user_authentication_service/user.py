#!/usr/bin/env python3
""" User model for managing users in the authentication service.
    This model maps to the 'users' table in the database.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


# Create the base class for the model
Base = declarative_base()


class User(Base):
    """
    User model representing the 'users' table in the database.

    Attributes:
        id: The primary key, an integer.
        email: A non-nullable string that stores the user's email.
        hashed_password: A non-nullable string for the hashed password.
        session_id: A nullable string for the session ID.
        reset_token: A nullable string for password reset tokens.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)
    hashed_password = Column(String(250), nullable=False)
    session_id = Column(String(250), nullable=True)
    reset_token = Column(String(250), nullable=True)
