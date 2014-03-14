"""Convienence functions for the Kipling Package Index server.

@author: Sam Pottinger (samnsparky)
@license: GNU GPL v3
"""

import random
import string

from werkzeug import security

PASS_SIZE = 10


def check_permissions(db_adapter, username, password, package=None):
    """Check a user's password and permissions to execute an operation.

    Verify a user's password is correct and, if a specific package is being
    modified, check that the user has permissions to modify that package.

    Returns False if:

     - The user does not exist in the system.
     - The user's password is incorrect.
     - A package was specified but does not exist.
     - The specified package does not list the user as an author.

    @param db_adapter: Wrapper around the application database.
    @type db_adapter: db_service.db_adapter
    @param username: The username of the user that wants to execute an
        operation.
    @param password: The password of the user that wants to execute an
        operation.
    @type password: str
    @keyword package: The name of the package that the user wants to modify.
        If None, will not check UAC for the package. Defaults to None.
    @type package: str
    """
    user_record = db_adapter.get_user(username)
    if not user_record:
        return False

    if not security.check_password_hash(user_record['password_hash'], password):
        return False

    if package:
        package_record = db_adapter.get_package(package)
        if not package_record:
            return False
        elif username in package_record['authors']:
            return True
        else:
            return False
    else:
        return True


def create_success_message(message):
    """Create a information message indicating that an operation executed.

    Create a dictionary that can be returned to the user after serialization
    indicating that an operation was successful on the server.

    @param message: Details about the successful execution.
    @type message: str
    @return: Dictionary encapsulating a status message.
    @rtype: dict
    """
    return {'success': True, 'message': message}


def create_error_message(message):
    """Create a information message indicating that an operation failed.

    Create a dictionary that can be returned to the user after serialization
    indicating that an operation was not successful on the server.

    @param message: Details about the failed execution.
    @type message: str
    @return: Dictionary encapsulating a status message.
    @rtype: dict
    """
    return {'success': False, 'message': message}


def generate_password():
    """Generate a random password.

    @return: Randomly generated password.
    @rtype: str
    """
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(PASS_SIZE))


def process_authors(record):
    """Process the authors section of the provided record of a package.

    If the authors section of the provided package record is still a CSV string
    as opposed to a Python-native list of authors, that CSV field will be
    interpreted, replacing that string with a list.

    @param record: The record whose authors field should be interpreted.
    @type record: dict
    """
    if isinstance(record['authors'], basestring):
        record['authors'] = record['authors'].replace(' ', '').split(',')
