from werkzeug.security import generate_password_hash, check_password_hash


def check_permissions(db_adapter, username, password, package=None):
    user_record = db_adapter.get_user(username)
    if not user_record:
        return False

    if not check_password_hash(user_record['password'], password):
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
    pass


def create_error_message(message):
    pass


def generate_password():
    pass
