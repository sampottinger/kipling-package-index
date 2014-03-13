import flask
from flask.ext.pymongo import PyMongo
from werkzeug.security import generate_password_hash

import db_service
import email_service
import util

app = flask.Flask(__name__)
mongo = PyMongo(app)
db_adapter = db_service.DBAdapter(mongo)


@app.route('/kpi/users.json', methods=['POST'])
def create_user():
    username = flask.request.form['username']
    email = flask.request.form['email']

    if db_adapter.get_user(username):
        return util.create_error_message(
            'A user with that username or email address already exists.'
        )

    if db_adapter.get_user_by_email(email):
        return util.create_error_message(
            'A user with that username or email address already exists.'
        )

    new_password = util.generate_password()
    password_hash = generate_password_hash(new_password)
    db_adapter.put_user({
        'username': username,
        'email': email,
        'password_hash': password_hash
    })
    email_service.send_password_email(username, new_password)
    return util.create_success_message('User account created.')


@app.route('/kpi/user/<username>.json', methods=['PUT'])
def update_user(username):
    old_password = flask.request.form['old_password']
    new_password = flask.request.form['new_password']

    if not db_adapter.get_user(username):
        return util.create_error_message(
            'Incorrect username or password provided.'
        )
    
    if not util.check_permissions(db_adapter, username, old_password):
        return util.create_error_message(
            'Incorrect username or password provided.'
        )

    password_hash = generate_password_hash(new_password)
    db_adapter.put_user({
        'username': username,
        'password_hash': password_hash
    })
    email_service.send_password_email(username)
    return util.create_success_message('User password updated.')


@app.route('/kpi/packages.json', methods=['POST'])
def create_package():
    record = {}
    form_info = flask.request.form

    if not check_permissions(form_info['username'], form_info['password']):
        return util.create_error_message('Username or password incorrect.')
    
    for field in db_service.ALLOWED_PACKAGE_FIELDS:
        if field in form_info:
            record[field] = form_info[field]

    for field in db_service.MINIMUM_REQUIRED_PACKAGE_FIELDS:
        if not field in record:
            return util.create_error_message(
                field + ' is required but not provided.'
            )

    if db_adapter.get_package(record['name']):
        return util.create_error_message(
            'A package by that name already exists.'
        )

    if not form_info['username'] in record['authors']:
        return util.create_error_message(
            'Your username must be in the author\'s list.'
        )

    db_adapter.put_package(record)
    return util.create_success_message('Package created.')


@app.route('/kpi/package/<package_name>.json', methods=['GET'])
def read_package():
    pass


@app.route('/kpi/package/<package_name>.json', methods=['PUT'])
def update_package():
    record = {}
    form_info = flask.request.form

    has_permissions = check_permissions(
        form_info['username'],
        form_info['password'],
        form_info['name']
    )
    if not has_permissions:
        return util.create_error_message('Username or password incorrect.')
    
    for field in db_service.ALLOWED_PACKAGE_FIELDS:
        if field in form_info:
            record[field] = form_info[field]

    for field in db_service.MINIMUM_REQUIRED_PACKAGE_FIELDS:
        if not field in record:
            return util.create_error_message(
                field + ' is required but not provided.'
            )

    if not form_info['username'] in record['authors']:
        return util.create_error_message(
            'Your username must be in the author\'s list.'
        )

    db_adapter.put_package(record)
    return util.create_success_message('Package updated.')


@app.route('/kpi/package/<package_name>.json', methods=['DELETE'])
def delete_package():
    pass


if __name__ == '__main__':
    app.run()