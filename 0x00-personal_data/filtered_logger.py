#!/usr/bin/env python3
"""
Module for logging and redacting PII fields from a database.
"""

import logging
import os
import mysql.connector
from typing import List
import re

# Define the fields considered as PII (Personally Identifiable Information)
PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(fields: List[
        str], redaction: str, message: str, separator: str) -> str:
    """
    Obfuscates specified fields in a log message.

    Args:
        fields (List[str]): List of field names to be obfuscated.
        redaction (str): The string to replace sensitive information with.
        message (str): The log message to be processed.
        separator (str): The character used to separate fields in the message.

    Returns:
        str: The log message with obfuscated fields.
    """
    for field in fields:
        pattern = rf'{field}=[^;]*{separator}'
        replacement = f'{field}={redaction}{separator}'
        message = re.sub(pattern, replacement, message)
    return message


class RedactingFormatter(logging.Formatter):
    """ Formatter class for filtering PII fields. """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """
        Initialize the formatter with fields to redact.
        """
        super().__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Filters values in incoming log records using filter_datum.

        Args:
            record (logging.LogRecord): Log record containing the message.

        Returns:
            str: The formatted and redacted log message.
        """
        original_message = super().format(record)
        return filter_datum(
            self.fields, self.REDACTION, original_message, self.SEPARATOR)


def get_logger() -> logging.Logger:
    """
    Creates and returns a logger named 'user_data' with custom settings.

    Returns:
        logging.Logger: A configured logger that redacts PII fields.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    handler = logging.StreamHandler()
    formatter = RedactingFormatter(fields=PII_FIELDS)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Returns a connector to the database using credentials
    from environment variables.

    Returns:
        mysql.connector.connection.MySQLConnection: A connection to the
        MySQL database.
    """
    db_username = os.getenv('PERSONAL_DATA_DB_USERNAME', 'root')
    db_password = os.getenv('PERSONAL_DATA_DB_PASSWORD', '')
    db_host = os.getenv('PERSONAL_DATA_DB_HOST', 'localhost')
    db_name = os.getenv('PERSONAL_DATA_DB_NAME')

    return mysql.connector.connect(
        user=db_username,
        password=db_password,
        host=db_host,
        database=db_name
    )


def main():
    """
    Main function to connect to the database, retrieve and log user data.
    """
    db = get_db()
    logger = get_logger()

    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users;")
        fields = cursor.column_names

        for row in cursor:
            message = " ".join(f"{k}={v};" for k, v in zip(fields, row))
            logger.info(message.strip())

    finally:
        cursor.close()
        db.close()


if __name__ == "__main__":
    main()
