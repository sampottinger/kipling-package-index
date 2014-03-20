"""Interface to the package index's datastore.

@author: Sam Pottinger
@license: GNU GPL v3
"""

import json

import pymongo

DATABASE_NAME = 'kpiserver'
PACKAGES_COLLECTION_NAME = 'packages'
USERS_COLLECTION_NAME = 'users'

MINIMUM_REQUIRED_USER_FIELDS = ['username', 'password_hash', 'email']
MINIMUM_REQUIRED_PACKAGE_FIELDS = [
    'authors',
    'license',
    'name',
    'humanName',
    'version'
]
ALLOWED_PACKAGE_FIELDS = [
    'authors',
    'license',
    'name',
    'humanName',
    'version',
    'description',
    'homepage',
    'repository'
]


class DBAdapter:
    """Dependency inversion adapter to make db access suck less."""

    def __init__(self, client):
        """Create a new database adapater around the database engine.

        @param client: The native database wrapper to adapt.
        @type client: flask.ext.pymongo.PyMongo
        """
        self.client = client

    def initialize_indicies(self):
        """Initialize indicies to improve access speeds for the database."""
        package_collection = self.get_package_collection()
        package_collection.ensure_index([('name', pymongo.ASCENDING)])

        users_collection = self.get_users_collection()
        users_collection.ensure_index([('username', pymongo.ASCENDING)])

    def get_database(self):
        """Get the database for the application.

        @return: Database point provided by the native pymongo.MongoClient
        @rtype: pymongo.database
        """
        return self.client.db[DATABASE_NAME]

    def get_package_collection(self):
        """Get the database collection for package information.

        @return: The mongodb database collection used to store package
            information.
        @rtype: pymongo.collection
        """
        return self.get_database()[PACKAGES_COLLECTION_NAME]

    def get_users_collection(self):
        """Get the database collection for user information.

        @return: The mongodb database collection used to store user information.
        @rtype: pymongo.collection
        """
        return self.get_database()[USERS_COLLECTION_NAME]

    def ensure_fields(self, record, fields):
        """Ensure a record has a series of fields.

        @param record: The (soon to be saved) database record to check.
        @type record: dict
        @param fields: List of fields that must be present.
        @type fields: list of str
        @raise ValueError: Raised if a field in the fields list is not in
            record.
        """
        for field in fields:
            if not field in record:
                raise ValueError('%s must be in this record.' % field)

    def get_package(self, package_name):
        """Get information about a specific package.

        @param package_name: The name (machine safe not humanName) of the
            package to look up.
        @type package_name: str
        @return: None if the package could not be found or a dictionary with
            package information.
        @rtype: dict
        """
        collection = self.get_package_collection()
        return collection.find_one({'name': package_name})

    def put_package(self, package_info):
        """Update or add information about a specific package.

        Adds a new record of a package in the index if a prior one does not
        exist. Otherwise, updates the prior entry. Fields not specified in the
        provided package_info but already present in the prior entry will
        remain untouched.

        @param package_info: Dictionary with package information. Will check
            that MINIMUM_REQUIRED_PACKAGE_FIELDS are present.
        @type package_info: dict
        """
        self.ensure(package_info, MINIMUM_REQUIRED_PACKAGE_FIELDS)
        name = package_info['name']
        collection = self.get_package_collection()
        collection.update({'name':name}, {'$set': package_info}, upsert=True)

    def delete_package(self, package_name):
        """Delete a package already in the index if it is in the index.

        Deletes a package from the index if that package was previously listed.
        Does nothing if the package specified is not in the index.

        @param package_name: The name of the package to delete.
        @type package_name: str
        """
        collection = self.get_package_collection()
        collection.remove({'name': package_name})

    def get_user(self, username):
        """Get information about a specific user.

        Get information about a specific user given that user's username. If
        one needs to lookup a user with their email address, see
        get_user_by_email.

        @param username: The name of the user to get information for.
        @type username: str
        @return: Record of the user in the application database. None if no
            matching found.
        @rtype: dict
        """
        collection = self.get_users_collection()
        return collection.find_one({'username': username})

    def get_user_by_email(self, email):
        """Get information about a specific user given an email address.

        Get information about a specific user given that user's email address.
        If one needs to lookup a user with their username, see get_user.

        @param email: The email address of the user to lookup.
        @type email: str
        @return: Record of the user in the application database. None if no
            matching found.
        @rtype: dict
        """
        collection = self.get_users_collection()
        return collection.find_one({'email': email})

    def put_user(self, user_info):
        """Put information about a user.

        Adds information about a new user to the index's user access controls
        system or replaces information about the user if a prior record exists
        by the same username.

        @param user_info: Record of the user to update. This will check that
            MINIMUM_REQUIRED_USER_FIELDS are present in this record.
        @type user_info: dict
        """
        self.ensure(user_info, MINIMUM_REQUIRED_USER_FIELDS)
        username = user_info['username']
        collection = self.get_user_collection()
        collection.update(
            {'username':username},
            {'$set': user_info},
            upsert=True
        )
