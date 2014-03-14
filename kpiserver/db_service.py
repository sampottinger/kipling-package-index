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

    def __init__(self, client):
        self.client = client

    def initialize_indicies(self):
        package_collection = self.get_package_collection()
        package_collection.ensure_index([('name', pymongo.ASCENDING)])

        users_collection = self.get_users_collection()
        users_collection.ensure_index([('username', pymongo.ASCENDING)])

    def get_database(self):
        return self.client.db[DATABASE_NAME]

    def get_package_collection(self):
        return self.get_database()[PACKAGES_COLLECTION_NAME]

    def get_users_collection(self):
        return self.get_database()[USERS_COLLECTION_NAME]

    def ensure_fields(self, record, fields):
        for field in fields:
            if not field in record:
                raise ValueError('%s must be in this record.' % field)

    def get_package(self, package_name):
        collection = self.get_package_collection()
        return collection.find_one({'name': package_name})

    def put_package(self, package_info):
        self.ensure(package_info, MINIMUM_REQUIRED_PACKAGE_FIELDS)
        name = package_info['name']
        collection = self.get_package_collection()
        collection.update({'name':name}, {'$set': package_info}, upsert=True)

    def delete_package(self, package_name):
        collection = self.get_package_collection()
        collection.remove({'name': package_name})

    def get_user(self, username):
        collection = self.get_users_collection()
        return collection.find_one({'username': username})

    def get_user_by_email(self, email):
        collection = self.get_users_collection()
        return collection.find_one({'email': email})

    def put_user(self, user_info):
        self.ensure(package_info, MINIMUM_REQUIRED_USER_FIELDS)
        username = user_info['username']
        collection = self.get_package_collection()
        collection.update(
            {'username':username},
            {'$set': user_info},
            upsert=True
        )
