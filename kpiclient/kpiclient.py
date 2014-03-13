"""Kipling Package Index command line tool.

Kipling Package Index command line tool that allows for basic management of user
accounts as well as create, read, update, and delete (CRUD) control over the
package index.


Create a package
----------------
Usage: ```kpicmd.py create [module] [path to module.json]  [path to zip]```  
Example: ```kpicmd.py create simple_ain ./module.json ./simple_ain_001.zip```

Read current information about a package
-----------------------------------------
Usage: ```kpicmd.py read [name of module]```  
Example: ```kpicmd.py read simple_ain```

Update a package
----------------
Usage: ```kpicmd.py update [module] [path to module.json] [path to zip]```  
Example: ```kpicmd.py update simple_ain ./module.json ./simple_ain_001.zip```

Delete a package  
----------------
Usage: ```kpicmd.py delete [name of module]```  
Example: ```kpicmd.py delete simple_ain```

Register a new username with KPI
--------------------------------
Usage: ```kpicmd.py useradd [username]```  
Example: ```kpicmd.py useradd samnsparky```

Update user password for KPI  
----------------------------
Usage: ```kpicmd.py passwd [username]```  
Example: ```kpicmd.py passwd samnsparky```


@author: Sam Pottinger (samnsparky)
@license: GNU GPL v3
"""

import getpass
import json
import sys

import requests

BASE_URL = 'https://kiplingwebservices.herokuapp.com/kpi/'
USERS_URL = BASE_URL + 'users.json'
USER_URL = BASE_URL + 'user/%s.json'
PACKAGES_URL = BASE_URL + 'packages.json'
PACKAGE_URL = BASE_URL + 'package/%s.json'

COMMAND_NOT_RECOGNIZED_ERR = '[Error] Command not recognized.'
PASSWORD_MISMATCH_ERR = 'New password and confirm password don\'t match.'
AUTHORS_FIELD_MISSING_ERR = 'authors field is required but missing in '\
                            'module.json.'
NAME_FIELD_MISSING_ERR = 'name field is required but missing in module.json'
HUMAN_NAME_FIELD_MISSING_ERR = 'humanName field is required but missing in '\
                               'module.json'
VERSION_FIELD_MISSING_ERR = 'version field is required but missing in '\
                               'module.json'
MODULE_JSON_MISSING_ERR = 'Could not load module.json.'
DEFAULT_LICENSE = 'GNU GPL v3'
parsed_response = 'Zip file not found or invalid.'

ROOT_HELP_TEXT = 'USAGE: kpicmd.py [command]'

HELP_TEXT = {
    'create': 'USAGE: kpicmd.py create [name of module] [path to module.json] '\
              '[path to zip archive]',
    'read': 'USAGE: kpicmd.py read [name of module]',
    'update': 'USAGE: kpicmd.py update [name of module] [path to module.json] '\
              '[path to zip archive]',
    'delete': 'USAGE: kpicmd.py delete [name of module]',
    'useradd': 'kpicmd.py useradd [username]',
    'passwd': 'kpicmd.py passwd [username]'
}

REQUIRED_PARAMS = {
    'create': 3,
    'read': 1,
    'update': 3,
    'delete': 1,
    'useradd': 1,
    'passwd': 1
}


class FakeResponse:
    """Wrapper that pretends to the be a response from requests HTTP lib.

    Wrapper that pretends to be a response from the Python requests HTTP lib,
    namely requests.models.Response.
    """

    def __init__(self, json_vals):
        """Create a new fake requests.models.Response.

        @param json_vals: The JSON values to pretend the server provided.
        @type json_vals: dict
        """
        self.json_vals = json_vals

    def json(self):
        """Return the JSON values that this is pretending the server provided.

        @return: The fake server response.
        @rtype: dict
        """
        return self.json_vals


class UserInfo:
    """Simple structure containing user authentication information."""

    def __init__(self, username, password):
        """Create new UserInfo structure.

        @param username: The name of the user being identified.
        @type username: str
        @param password: The password to authenticate the user with.
        @type password: str
        """
        self.username = username
        self.password = password


def generate_error(error):
    """Generate a fake response from the server reporting an error.

    @param error: The error message to report.
    @type error: str
    @return: Fake response prentending to be a server response reporting an
        error.
    @rtype: FakeResponse
    """
    return FakeResponse({'success': False, 'message': error})


def get_module_json(path):
    """Load a JSON file.

    @param path: The path to the JSON file.
    @type path: str
    @return: The JSON file contents or None if the file could not be open
        because of a file operation error (IOError) or JSON parse error
        (ValueError).
    @rtype: None or dict
    """
    try:
        with open(path) as f:
            return json.load(f)
    except (IOError, ValueError):
        return None


def upload_zip_file(local_path, remote_url, upload_spec):
    """Upload a zip file containing module information and source.

    @param local_path: The path to the local zip archive to upload.
    @type local_path: str
    @param remote_url: The URL to post the zip archive to.
    @type remote_url: str
    @param upload_spec: Dictionary with (likely S3) credentials or temporary
        access keys.
    @type upload_spec: dict
    @return: The repsonse returned from the uploads service.
    @rtype: requests.models.Response
    """
    files = {'file': open(local_path, 'rb')}
    return requests.post(remote_url, files=files, data=upload_spec)


def add_user_info(user_info, info_dict):
    """Adds user info to a dictionary to use with HTTP requests.

    @param user_info: The user info object to copy to the info dictionary.
    @type user_info: UserInfo
    @param info_dict: Info dictionary to add the user info to.
    @type info_dict: dict
    """
    info_dict['username'] = user_info.username
    info_dict['password'] = user_info.password


def parse_response(response):
    """Parse the JSON payload from a requests.models.Response.

    @return: JSON dictionary loaded from a response.
    @rtype: dict
    """
    return response.json()


def internal_print_table(values):
    """Print a pretty display with information about a package in the index.

    @param values: The information about the package.
    @type values: dict
    """
    description = values['description']
    print description
    print ''

    table = prettytable.PrettyTable(['Field', 'Value'])
    table.align['Field'] = 'l'

    authors = ', '.join(values['authors'])
    table.add_row(['authors', authors])

    license = values['license']
    table.add_row(['license', license])

    homepage = values['homepage']
    table.add_row(['homepage', homepage])

    repository = values['repository']
    table.add_row(['repository', repository])

    print table


def deploy(user_info, package_name, module_json_path, zip_path, new_entry):
    """Deploy a package to the package index.

    @param package_name: The name of the package to post to the package index.
    @type package_name: str
    @param module_json_path: Path to the JSON file (module.json) describing the
        module (package) to upload.
    @type module_json_path: str
    @param zip_path: Path to the ZIP file to upload.
    @type zip_path: str
    @param new_entry: Flag indicating if this should be an entirely new package.
    @type new_entry: bool
    @return: Response from the server for the original (not file upload)
        request.
    @rtype: requests.models.Response
    """
    json_info = get_module_json(module_json_path)
    if not json_info:
        return generate_error(MODULE_JSON_MISSING_ERR)

    if not 'name' in json_info:
        return generate_error(NAME_FIELD_MISSING_ERR)

    if not 'humanName' in json_info:
        return generate_error(HUMAN_NAME_FIELD_MISSING_ERR)

    if not 'version' in json_info:
        return generate_error(VERSION_FIELD_MISSING_ERR)

    if not 'authors' in json_info:
        return generate_error(AUTHORS_FIELD_MISSING_ERR)

    if not 'license' in json_info:
        json_info['license'] = DEFAULT_LICENSE

    add_user_info(user_info, json_info)

    if new_entry:
        response = requests.post(PACKAGES_URL, data=json_info)
    else:
        response = requests.put(PACKAGE_URL % json_info['name'], data=json_info)

    parsed_response = parse_response(response)
    if not parsed_response['success']:
        return parsed_response

    upload_url = parsed_response['upload_url']
    upload_spec = parsed_response['upload_spec']
    zip_file_response = upload_zip_file(zip_path, upload_url, upload_spec)
    if not zip_file_response:
        return generate_error(ZIP_FILE_NOT_FOUND)

    return response


def create(user_info, package_name, module_json_path, zip_path):
    """Create a new package within the index.

    @param package_name: The name of the package to post to the package index.
    @type package_name: str
    @param module_json_path: Path to the JSON file (module.json) describing the
        module (package) to upload.
    @type module_json_path: str
    @param zip_path: Path to the ZIP file to upload.
    @type zip_path: str
    @return: Response from the server for the original (not file upload)
        request.
    @rtype: requests.models.Response
    """
    return deploy(user_info, package_name, module_json_path, zip_path, True)


def read(package_name):
    """Request and print information about a package.

    @param package_name: The name of the package to lookup.
    @type package_name: str
    @return: The response from HTTP request to the package index.
    @rtype: requests.models.Response
    """
    response = requests.get(PACKAGE_URL % package_name)
    parsed_response = parse_response(response)

    if not parsed_response['success']:
        return parsed_response

    internal_print_table(parsed_response['record'])
    return parse_response


def update(user_info, package_name, module_json_path, zip_path):
    """Update an existing package within the index.

    @param package_name: The name of the package to post to the package index.
    @type package_name: str
    @param module_json_path: Path to the JSON file (module.json) describing the
        module (package) to upload.
    @type module_json_path: str
    @param zip_path: Path to the ZIP file to upload.
    @type zip_path: str
    @return: Response from the server for the original (not file upload)
        request.
    @rtype: requests.models.Response
    """
    return deploy(user_info, package_name, module_json_path, zip_path, False)


def delete(user_info, package_name):
    """Delete a package from the index.

    @param user_info: Authentication information about the user who is making
        this request.
    @type user_info: UserInfo
    @return: Response from the server for the original HTTP request.
    @rtype: requests.models.Response
    """
    payload = {'name': package_name}
    add_user_info(user_info, payload)
    return requests.delete(PACKAGE_URL % package_name, data=payload)


def useradd(username, email):
    """Add a new user to the package index user access control system.

    @param username: The name of the user to add to the package index.
    @type username: str
    @return: Response from the server for the original HTTP request.
    @rtype: requests.models.Response
    """
    payload = {'username': username, 'email': email}
    return requests.post(USERS_URL, data=payload)


def passwd(username, old_password, new_password, confirm_password):
    """Change the password for a user in the package UAC system.

    Change the password for a user in the package index's user access control
    system.

    @param username: The name of the user whose password should be changed.
    @type username: str
    @param old_password: The old password for the user.
    @type old_password: str
    @param new_password: The new password for the user.
    @type new_password: str
    @param confirm_password: Confirmation of the new password for the user. Will
        not execute if confirm_password != new_password.
    @type confirm_password: str
    @return: Response from the server for the original HTTP request.
    @rtype: requests.models.Response
    """
    if new_password != confirm_password:
        return generate_error(PASSWORD_MISMATCH_ERR)

    payload = {
        'username': username,
        'old_password': old_password,
        'new_password': new_password
    }
    return requests.post(USER_URL % username, data=payload)


def get_params(num_params):
    """Get the parameters for the selected command.

    @param num_params: The number of parameters to check for.
    @type num_params: int
    @return: None if not enough parameters were provided or the list of
        arguments for the command if enough parameters were provided (excludes
        the name of the script and the provided command).
    @rtype: iterable over str
    """
    num_params = len(sys.argv) - 2
    if num_params < num_params:
        return None
    else:
        return sys.argv[2:]


def main_create():
    """Main program driver for creating a new listing entry.

    @return: Response from the server for the original HTTP request.
    @rtype: requests.models.Response
    """
    params = get_params(REQUIRED_PARAMS['create'])
    if not params:
        print HELP_TEXT['create']
        return False

    module_name = params[0]
    path_to_module = params[1]
    path_to_zip = params[2]

    username = raw_input('Username: ')
    password = getpass.getpass()

    user_info = UserInfo(username, password)
    return create(user_info, module_name, path_to_module, path_to_zip)


def main_read():
    """Main program driver for reading an existing listing entry.

    @return: Response from the server for the original HTTP request.
    @rtype: requests.models.Response
    """
    params = get_params(REQUIRED_PARAMS['read'])
    if not params:
        print HELP_TEXT['read']
        return False

    module_name = params[0]
    return read(module_name)


def main_update():
    """Main program driver for updating an existing listing entry.

    @return: Response from the server for the original HTTP request.
    @rtype: requests.models.Response
    """
    params = get_params(REQUIRED_PARAMS['update'])
    if not params:
        print HELP_TEXT['update']
        return False

    module_name = params[0]
    path_to_module = params[1]
    path_to_zip = params[2]

    username = raw_input('Username: ')
    password = getpass.getpass()

    user_info = UserInfo(username, password)
    return update(user_info, module_name, path_to_module, path_to_zip)


def main_delete():
    """Main program driver for deleting an existing entry.

    @return: Response from the server for the original HTTP request.
    @rtype: requests.models.Response
    """
    params = get_params(REQUIRED_PARAMS['delete'])
    if not params:
        print HELP_TEXT['delete']
        return False

    module_name = params[0]
    username = raw_input('Username: ')
    password = getpass.getpass()

    user_info = UserInfo(username, password)
    return delete(user_info, module_name)


def main_useradd():
    """Main program driver for adding a user to the listing UAC service.

    Main program driver for adding a user to the listing's user access control
    service.

    @return: Response from the server for the original HTTP request.
    @rtype: requests.models.Response
    """
    params = get_params(REQUIRED_PARAMS['useradd'])
    if not params:
        print HELP_TEXT['useradd']
        return False

    username = params[0]

    email_address = raw_input('Email address: ')

    return useradd(username, email_address)


def main_passwd():
    """Main program driver for updating a user's password.

    Main program driver for updating a user's password within the listing's user
    access control service.

    @return: Response from the server for the original HTTP request.
    @rtype: requests.models.Response
    """
    params = get_params(REQUIRED_PARAMS['passwd'])
    if not params:
        print HELP_TEXT['passwd']
        return False

    username = params[0]
    current_password = getpass.getpass()
    new_password = getpass.getpass('New password: ')
    confirm_new = getpass.getpass('Confirm new password: ')

    return passwd(username, current_password, new_password, confirm_new)


def main():
    """Top level main program driver."""
    if len(sys.argv) < 2:
        print ROOT_HELP_TEXT
        return

    command = sys.argv[1]
    if not command in COMMANDS:
        print COMMAND_NOT_RECOGNIZED_ERR
        return

    result = COMMANDS[command]()
    if not result['success']:
        print '[Error] ' + result['message']
        return
    else:
        print '[Success] ' + result['message']


COMMANDS = {
    'create': main_create,
    'read': main_read,
    'update': main_update,
    'delete': main_delete,
    'useradd': main_useradd,
    'passwd': main_passwd
}


if __name__ == '__main__':
    main()
