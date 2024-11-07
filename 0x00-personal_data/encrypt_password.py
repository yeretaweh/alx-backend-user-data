#!/usr/bin/env python3
"""
Module for password hashing and validation using bcrypt
"""

import bcrypt


def hash_password(password: str) -> bytes:
    """
    Hash a password with a salted bcrypt hash.

    Args:
        password (str): The password to hash.

    Returns:
        bytes: The salted, hashed password.
    """
    # Encode the password to bytes
    password_bytes = password.encode('utf-8')
    # Generate a salt and hash the password
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_password


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    Check if the provided password matches the hashed password.

    Args:
        hashed_password (bytes): The hashed password to check against.
        password (str): The password to validate.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    # Encode the password to bytes
    password_bytes = password.encode('utf-8')
    # Check if the hashed password matches the provided password
    return bcrypt.checkpw(password_bytes, hashed_password)


# Example usage
if __name__ == "__main__":
    import sys

    password = "MyAmazingPassw0rd"
    encrypted_password = hash_password(password)
    print(encrypted_password)
    print(is_valid(encrypted_password, password))
