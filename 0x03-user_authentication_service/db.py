#!/usr/bin/env python3
"""DB module for managing the database connetion and user management."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from user import Base, User
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError


class DB:
    """DB class for interacting with the database."""

    def __init__(self) -> None:
        """Initialize a new DB instance."""
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized sessio object for database interaction."""
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Add a new user to the database.

        Args:
            email (str): The email of the user.
            hashed_password (str): The hashed password of the user.

        Returns:
            User: The newly created User object.
        """
        new_user = User(email=email, hashed_password=hashed_password)
        self._session.add(new_user)  # Add the user to the session
        self._session.commit()  # Commit the transaction to save the user
        return new_user

    def find_user_by(self, **kwargs) -> User:
        """Find the first user in the DB that matches the filters in kwargs.

        Args:
            **kwargs: Arbitrary keyword arguments to filter the query by.

        Returns:
            User: The First User found that matches the filters in kwargs.

        Raises:
            NoResultFound: If no user is found that matches
            the filters in kwargs.
            InvalidRequestError: If invalid arguments are passed.
        """
        try:
            # Query the DB and filter by the keyword arguments (kwargs)
            user = self._session.query(User).filter_by(**kwargs).first()
            if user is None:
                raise NoResultFound
            return user
        except AttributeError:
            raise InvalidRequestError

    def update_user(self, user_id: int, **kwargs) -> None:
        """Finds a user by id, then updates the User object with kwargs."""

        # First find the user by id
        user = self.find_user_by(id=user_id)

        for key, value in kwargs.items():
            # Check if the parameter is a valid user attribute
            if not hasattr(user, key):
                # Raise ValueError if not
                raise ValueError
            # Now update the user with the provided valid kwargs
            setattr(user, key, value)

        # Commit the update to save changes
        self._session.commit()
