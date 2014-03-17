"""Routes and top level controllers for the Kipling Package Index server.

Routes and top level controllers for the server to manage the Kipling Package
Index information including user accounts, package info, and package zip
archive uploads.

@author: Sam Pottinger (samnsparky)
@license: GNU GPL v3
"""
import json

import flask
from flask.ext.pymongo import PyMongo
from werkzeug.security import generate_password_hash

import db_service
import email_service
import util

app = flask.Flask(__name__)


@app.route('/kpi/users.json', methods=['POST'])
def create_user():
    """Creates a new user in the package index's user access controls system.

    Create a new user in the user access controls service for the package index.
    This causes an email to be sent to the new user with a temporary password.

    Form-encdoded params:

     - ```username``` The name of the new user.
     - ```email``` The email address for the new user.

    JSON-document returned:

     - ```success``` Boolean value indicating if successful. Will be true if new
       user created and false otherwise.
     - ```message``` Deatails about the result of the operation. Will be
       provided in both the success and failure cases.

    @return: JSON document
    @rtype: flask.response
    """
    username = flask.request.form['username']
    email = flask.request.form['email']

    if db_adapter.get_user(username):
        return json.dumps(util.create_error_message(
            'A user with that username or email address already exists.'
        ))

    if db_adapter.get_user_by_email(email):
        return json.dumps(util.create_error_message(
            'A user with that username or email address already exists.'
        ))

    new_password = util.generate_password()
    password_hash = generate_password_hash(new_password)
    db_adapter.put_user({
        'username': username,
        'email': email,
        'password_hash': password_hash
    })
    email_service.send_password_email(app, email, username, new_password)
    return json.dumps(util.create_success_message('User account created.'))


@app.route('/kpi/user/<username>.json', methods=['PUT'])
def update_user(username):
    """Updates the information about a user in the package index.

    Updates a user in the user access controls service for the package index.
    This includes modifying the user's password.

    Form-encdoded params:

     - ```username``` The name of the user to update.
     - ```old_password``` The current password for the user.
     - ```new_password``` The password to assign to the user.

    JSON-document returned:

     - ```success``` Boolean value indicating if successful. Will be true if the
       user was updated and false otherwise.
     - ```message``` Details about the result of the operation. Will be provided
       in both the success and failure cases.

    @param username: The name of the user to modify as read from the url.
    @type username: str
    @return: JSON document
    @rtype: flask.response
    """
    old_password = flask.request.form['old_password']
    new_password = flask.request.form['new_password']

    if not db_adapter.get_user(username):
        return json.dumps(util.create_error_message(
            'Incorrect username or password provided.'
        ))

    if not util.check_permissions(db_adapter, username, old_password):
        return json.dumps(util.create_error_message(
            'Incorrect username or password provided.'
        ))

    password_hash = generate_password_hash(new_password)
    db_adapter.put_user({
        'username': username,
        'password_hash': password_hash
    })

    user_info = db_adapter.get_user(username)

    email_service.send_password_email(app, user_info['email'], username)
    return json.dumps(util.create_success_message('User password updated.'))


@app.route('/kpi/packages.json', methods=['POST'])
def create_package():
    """Create a new package in the Kipling package index.

    Create a new package in the index. No prior packages may have the same name
    and the submitting user must be in the authors list.

    Form-encoded params:

     - ```username``` The username of the user who is creating a new package.
     - ```password``` The password of the user who is creating a new package.
     - ```authors``` CSV list of usernames who have authorial access to this
       package.
     - ```license``` String description of the license the package is released
       under (like MIT or GNU GPL v3)
     - ```name``` The machine safe name (any valid javascript identifier) of the
       package. 
     - ```humanName``` The name of the package to present to the user (can be
       any valid string).
     - ```version``` The major.minor.incremental (ex: 1.2.34) version number
       that this package is currently releasing.
     - May also include module.json fields listed in README for kpiclient.

    JSON-document returned:

     - ```success``` Boolean value indicating if successful. Will be true if the
       package was created and false otherwise.
     - ```message``` Details about the result of the operation. Will be provided
       in both the success and failure cases.

    @return: JSON document
    @rtype: flask.response
    """
    record = {}
    form_info = flask.request.form

    has_permissions = util.check_permissions(
        db_adapter,
        form_info['username'],
        form_info['password']
    )
    if not has_permissions:
        return json.dumps(
            util.create_error_message('Username or password incorrect.')
        )

    for field in db_service.ALLOWED_PACKAGE_FIELDS:
        if field in form_info:
            record[field] = form_info[field]

    for field in db_service.MINIMUM_REQUIRED_PACKAGE_FIELDS:
        if not field in record:
            return json.dumps(util.create_error_message(
                field + ' is required but not provided.'
            ))

    if db_adapter.get_package(record['name']):
        return json.dumps(util.create_error_message(
            'A package by that name already exists.'
        ))

    util.process_authors(record)
    if not form_info['username'] in record['authors']:
        return json.dumps(util.create_error_message(
            'Your username must be in the author\'s list.'
        ))

    db_adapter.put_package(record)
    return json.dumps(util.create_success_message('Package created.'))


@app.route('/kpi/package/<package_name>.json', methods=['GET'])
def read_package(package_name):
    """Read information about a package already in the index.

    Form-encoded params: none

    JSON-document returned:

     - ```successful``` Boolean indicating if the package was found and read
       successfully.
     - ```message``` Information about the error encountered. Blank if no error.
     - ```authors``` CSV list of usernames who have authorial access to this
       package.
     - ```license``` String description of the license the package is released
       under (like MIT or GNU GPL v3)
     - ```record``` Information about the package.
       - ```name``` The machine safe name (any valid javascript identifier) of
         the package.
       - ```humanName``` The name of the package to present to the user (can be
         any valid string).
       - ```version``` The major.minor.incremental (ex: 1.2.34) version number
         that this package is currently releasing.
       - ```description``` Human-friendly short description of the package. May
         contain markdown and may be a blank string.
       - ```homepage``` The URL to a website with more information for this
         package. May be a blank string.
       - ```repository``` The URL to a repository with the source for this
         package. May be a blank string.

    @param package_name: The name of the package to retrieve information about.
    @type package_name: str
    @return: JSON document
    @rtype: flask.response
    """
    package = db_adapter.get_package(package_name)
    if package:
        return json.dumps({'success': True, 'record': package})
    else:
        return json.dumps(
            util.create_error_message('Package not found in the index.')
        )


@app.route('/kpi/package/<package_name>.json', methods=['PUT'])
def update_package(package_name):
    """Update information about a package already in the index.

    Update an existing package in the index. A prior packages must have the same
    name, the submitting user must have permissions to edit that package, and
    the submitting user must be in the authors list.

    Form-encoded params:  

     - ```username``` The username of the user who is updating the package.
     - ```password``` The password of the user who is updating the package.
     - ```authors``` CSV list of usernames who have authorial access to this
       package.
     - ```license``` String description of the license the package is released
       under (like MIT or GNU GPL v3)
     - ```name``` The machine safe name (any valid javascript identifier) of the
       package. 
     - ```humanName``` The name of the package to present to the user (can be
       any valid string).
     - ```version``` The major.minor.incremental (ex: 1.2.34) version number
       that this package is currently releasing.
     - May also include module.json fields listed in README for kpiclient.

    JSON-document returned:

     - ```success``` Boolean value indicating if successful. Will be true if the
       package was updated and false otherwise.
     - ```message``` Details about the result of the operation. Will be provided
       in both the success and failure cases.

    @param package_name: The name of the package to update.
    @type package_name: str
    @return: JSON document
    @rtype: flask.response
    """
    record = {}
    form_info = flask.request.form

    has_permissions = util.check_permissions(
        db_adapter,
        form_info['username'],
        form_info['password'],
        package_name
    )
    if not has_permissions:
        msg = util.create_error_message(
            'Username, password, or package name incorrect.'
        )
        return json.dumps(msg)

    for field in db_service.ALLOWED_PACKAGE_FIELDS:
        if field in form_info:
            record[field] = form_info[field]

    for field in db_service.MINIMUM_REQUIRED_PACKAGE_FIELDS:
        if not field in record:
            return json.dumps(util.create_error_message(
                field + ' is required but not provided.'
            ))

    util.process_authors(record)
    db_adapter.put_package(record)
    return json.dumps(util.create_success_message('Package updated.'))


@app.route('/kpi/package/<package_name>.json/delete', methods=['POST'])
def delete_package(package_name):
    """Remove a package from the index.

    Remove a new package from the the index. A prior packages must have the same
    name and the submitting user must have permissions to edit that package.

    Form-encoded params:

     - ```username``` The username of the user who is deleting the package.
     - ```password``` The password of the user who is deleting the package.

    JSON-document returned:

     - ```success``` Boolean value indicating if successful. Will be true if the
       package was updated and false otherwise.
     - ```message``` Details about the result of the operation. Will be provided
       in both the success and failure cases.

    @return: JSON document
    @rtype: flask.response
    """
    has_permissions = util.check_permissions(
        db_adapter,
        flask.request.form['username'],
        flask.request.form['password'],
        package_name
    )
    if not has_permissions:
        msg = util.create_error_message(
            'Username, password, or package name incorrect.'
        )
        return json.dumps(msg)

    db_adapter.delete_package(package_name)
    return json.dumps(util.create_success_message('Package deleted.'))


if __name__ == '__main__':
    mongo = PyMongo(app)
    db_adapter = db_service.DBAdapter(mongo)
    app.run()
