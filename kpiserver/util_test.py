"""Tests for convienence functions for the Kipling Package Index server.

@author: Sam Pottinger (samnsparky)
@license: GNU GPL v3
"""

import unittest

import mox
from werkzeug import security

import db_service
import util

TEST_USERNAME = 'username'
TEST_PASSWORD = 'password'
TEST_PASSWORD_HASH = 'hash'
TEST_USER = {'username': TEST_USERNAME, 'password_hash': TEST_PASSWORD_HASH}
TEST_PACKAGE_NAME = 'package'
PACKAGE_NO_USER = {'authors': []}
PACKAGE_WITH_USER = {'authors': [TEST_USERNAME]}


class UtilTests(mox.MoxTestBase):

    def test_check_permissions_no_user(self):
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)
        test_adapter.get_user(TEST_USERNAME).AndReturn(None)
        self.mox.ReplayAll()

        result = util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.assertFalse(result)

    def test_check_permissions_incorrect_password(self):
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)
        test_adapter.get_user(TEST_USERNAME).AndReturn(TEST_USER)

        self.mox.StubOutWithMock(security, 'check_password_hash')
        security.check_password_hash(
            TEST_PASSWORD_HASH,
            TEST_PASSWORD
        ).AndReturn(False)

        self.mox.ReplayAll()

        result = util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.assertFalse(result)

    def test_check_permissions_success_no_package(self):
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)
        test_adapter.get_user(TEST_USERNAME).AndReturn(TEST_USER)

        self.mox.StubOutWithMock(security, 'check_password_hash')
        security.check_password_hash(
            TEST_PASSWORD_HASH,
            TEST_PASSWORD
        ).AndReturn(True)

        self.mox.ReplayAll()

        result = util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            TEST_PASSWORD
        )
        self.assertTrue(result)

    def test_check_permissions_package_not_found(self):
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)
        test_adapter.get_user(TEST_USERNAME).AndReturn(TEST_USER)
        test_adapter.get_package(TEST_PACKAGE_NAME).AndReturn(None)

        self.mox.StubOutWithMock(security, 'check_password_hash')
        security.check_password_hash(
            TEST_PASSWORD_HASH,
            TEST_PASSWORD
        ).AndReturn(True)

        self.mox.ReplayAll()

        result = util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            TEST_PASSWORD,
            TEST_PACKAGE_NAME
        )
        self.assertFalse(result)

    def test_check_permissions_not_author(self):
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)
        test_adapter.get_user(TEST_USERNAME).AndReturn(TEST_USER)
        test_adapter.get_package(TEST_PACKAGE_NAME).AndReturn(PACKAGE_NO_USER)

        self.mox.StubOutWithMock(security, 'check_password_hash')
        security.check_password_hash(
            TEST_PASSWORD_HASH,
            TEST_PASSWORD
        ).AndReturn(True)

        self.mox.ReplayAll()

        result = util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            TEST_PASSWORD,
            TEST_PACKAGE_NAME
        )
        self.assertFalse(result)

    def test_check_permissions_success_with_package(self):
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)
        test_adapter.get_user(TEST_USERNAME).AndReturn(TEST_USER)
        test_adapter.get_package(TEST_PACKAGE_NAME).AndReturn(PACKAGE_WITH_USER)

        self.mox.StubOutWithMock(security, 'check_password_hash')
        security.check_password_hash(
            TEST_PASSWORD_HASH,
            TEST_PASSWORD
        ).AndReturn(True)

        self.mox.ReplayAll()

        result = util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            TEST_PASSWORD,
            TEST_PACKAGE_NAME
        )
        self.assertTrue(result)

    def test_create_success_message(self):
        result = util.create_success_message('message')
        self.assertTrue(result['success'])

    def test_create_error_message(self):
        result = util.create_error_message('message')
        self.assertFalse(result['success'])

    def test_generate_password(self):
        password = util.generate_password()
        self.assertNotEqual(password, None)

    def test_process_authors_already_interpreted(self):
        record = {'authors': ['user1', 'user2']}
        util.process_authors(record)
        self.assertEqual(record['authors'], ['user1', 'user2'])

    def test_process_authors_not_interpreted(self):
        record = {'authors': 'user1, user2'}
        util.process_authors(record)
        self.assertEqual(record['authors'], ['user1', 'user2'])

    def test_process_authors_single_author_str(self):
        record = {'authors': 'user1'}
        util.process_authors(record)
        self.assertEqual(record['authors'], ['user1'])

    def test_process_authors_single_author_list(self):
        record = {'authors': ['user1']}
        util.process_authors(record)
        self.assertEqual(record['authors'], ['user1'])


if __name__ == '__main__':
    unittest.main()
