"""Automated tests for the Kipling Package Index server.

@author: Sam Pottinger (samnsparky)
@author: Rory Olsen (rolsen)
@license: GNU GPL v3
"""
import copy
import json
import unittest

import mox

import db_service
import email_service
import kpiserver
import util

TEST_PASSWORD = 'crackme'
TEST_OTHER_USERNAME = 'otheruser'
TEST_USERNAME = 'testuser'
TEST_HASH = 'dahash'
TEST_EMAIL = 'test@example.com'
TEST_USER = {
    'username': TEST_USERNAME,
    'password_hash': TEST_HASH,
    'email': TEST_EMAIL
}

TEST_LICENSE = 'license'
TEST_NAME = 'name'
TEST_HUMAN_NAME = 'humanName'
TEST_VERSION = '0.1.2'

TEST_AUTHORS_MISSING = [TEST_OTHER_USERNAME]
TEST_AUTHORS_MISSING_STR = ','.join(TEST_AUTHORS_MISSING)
TEST_AUTHORS_INCLUSIVE = [TEST_OTHER_USERNAME, TEST_USERNAME]
TEST_AUTHORS_INCLUSIVE_STR = ','.join(TEST_AUTHORS_INCLUSIVE)

TEST_PACKAGE = {
    'license': TEST_LICENSE,
    'name': TEST_NAME,
    'humanName': TEST_HUMAN_NAME,
    'version': TEST_VERSION,
    'authors': TEST_AUTHORS_INCLUSIVE
}


class KPIServerTests(mox.MoxTestBase):

    def setUp(self):
        mox.MoxTestBase.setUp(self)
        self.app = kpiserver.app.test_client()
        kpiserver.app.config['DEBUG'] = True

    def test_create_user_prior_username(self):
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)
        test_adapter.get_user(TEST_USERNAME).AndReturn(TEST_USER)
        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.post('/kpi/users.json', data=dict(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        ))

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertFalse(json_result['success'])

    def test_create_user_prior_email(self):
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)
        test_adapter.get_user(TEST_USERNAME).AndReturn(None)
        test_adapter.get_user_by_email(TEST_EMAIL).AndReturn(TEST_USER)
        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.post('/kpi/users.json', data=dict(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        ))

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertFalse(json_result['success'])

    def test_create_user_success(self):
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)
        test_adapter.get_user(TEST_USERNAME).AndReturn(None)
        test_adapter.get_user_by_email(TEST_EMAIL).AndReturn(None)

        test_adapter.put_user({
            'username': TEST_USERNAME,
            'email': TEST_EMAIL,
            'password_hash': mox.IsA(basestring)
        })

        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.post('/kpi/users.json', data=dict(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        ))

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertTrue(json_result['success'])

    def test_update_user_no_user(self):
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)
        test_adapter.get_user(TEST_USERNAME).AndReturn(None)
        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.put('/kpi/user/%s.json' % TEST_USERNAME, data=dict(
            old_password='oldpass',
            new_password='newpass'
        ))

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertFalse(json_result['success'])

    def test_update_user_invalid_password(self):
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)
        test_adapter.get_user(TEST_USERNAME).AndReturn(TEST_USER)

        self.mox.StubOutWithMock(util, 'check_permissions')
        util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            'oldpass'
        ).AndReturn(False)
        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.put('/kpi/user/%s.json' % TEST_USERNAME, data=dict(
            old_password='oldpass',
            new_password='newpass'
        ))

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertFalse(json_result['success'])

    def test_update_user_success(self):
        self.mox.StubOutWithMock(util, 'check_permissions')
        self.mox.StubOutWithMock(email_service, 'send_password_email')
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)

        # Get through UAC
        test_adapter.get_user(TEST_USERNAME).AndReturn(TEST_USER)
        util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            'oldpass'
        ).AndReturn(True)

        # Update the user
        test_adapter.put_user({
            'username': TEST_USERNAME,
            'password_hash': mox.IsA(basestring)
        })

        # Get email address for user and send password update
        test_adapter.get_user(TEST_USERNAME).AndReturn(TEST_USER)
        email_service.send_password_email(TEST_EMAIL, TEST_USERNAME)

        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.put('/kpi/user/%s.json' % TEST_USERNAME, data=dict(
            old_password='oldpass',
            new_password='newpass'
        ))

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertTrue(json_result['success'])

    def test_create_package_invalid_password(self):
        self.mox.StubOutWithMock(util, 'check_permissions')
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)

        util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            TEST_PASSWORD
        ).AndReturn(False)

        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.post('/kpi/packages.json', data=dict(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            authors=TEST_AUTHORS_INCLUSIVE_STR,
            license=TEST_LICENSE,
            name=TEST_NAME,
            humanName=TEST_HUMAN_NAME,
            version=TEST_VERSION
        ))

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertFalse(json_result['success'])

    def test_create_package_prior_name(self):
        self.mox.StubOutWithMock(util, 'check_permissions')
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)

        util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            TEST_PASSWORD
        ).AndReturn(True)

        test_adapter.get_package(TEST_NAME).AndReturn(TEST_PACKAGE)

        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.post('/kpi/packages.json', data=dict(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            authors=TEST_AUTHORS_INCLUSIVE_STR,
            license=TEST_LICENSE,
            name=TEST_NAME,
            humanName=TEST_HUMAN_NAME,
            version=TEST_VERSION
        ))

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertFalse(json_result['success'])

    def test_create_package_not_author(self):
        self.mox.StubOutWithMock(util, 'check_permissions')
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)

        util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            TEST_PASSWORD
        ).AndReturn(True)

        test_adapter.get_package(TEST_NAME).AndReturn(None)

        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.post('/kpi/packages.json', data=dict(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            authors=TEST_AUTHORS_MISSING_STR,
            license=TEST_LICENSE,
            name=TEST_NAME,
            humanName=TEST_HUMAN_NAME,
            version=TEST_VERSION
        ))

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertFalse(json_result['success'])

    def test_create_package_success(self):
        self.mox.StubOutWithMock(util, 'check_permissions')
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)

        util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            TEST_PASSWORD
        ).AndReturn(True)

        test_adapter.get_package(TEST_NAME).AndReturn(None)

        test_adapter.put_package(TEST_PACKAGE)

        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.post('/kpi/packages.json', data=dict(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            authors=TEST_AUTHORS_INCLUSIVE_STR,
            license=TEST_LICENSE,
            name=TEST_NAME,
            humanName=TEST_HUMAN_NAME,
            version=TEST_VERSION
        ))

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertTrue(json_result['success'])

    def test_read_package_not_found(self):
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)
        test_adapter.get_package(TEST_NAME).AndReturn(None)

        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.get("/kpi/package/%s.json" % TEST_NAME)

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertFalse(json_result['success'])

    def test_read_package_success(self):
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)
        test_adapter.get_package(TEST_NAME).AndReturn(TEST_PACKAGE)

        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.get("/kpi/package/%s.json" % TEST_NAME)

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertTrue(json_result['success'])

    def test_update_package_fail_uac(self):
        self.mox.StubOutWithMock(util, 'check_permissions')
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)

        util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            TEST_PASSWORD,
            TEST_NAME
        ).AndReturn(False)

        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.put('/kpi/package/%s.json' % TEST_NAME, data=dict(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            authors=TEST_AUTHORS_MISSING_STR,
            license=TEST_LICENSE,
            humanName=TEST_HUMAN_NAME,
            name=TEST_NAME,
            version=TEST_VERSION
        ))

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertFalse(json_result['success'])

    def test_update_package_success(self):
        self.mox.StubOutWithMock(util, 'check_permissions')
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)

        util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            TEST_PASSWORD,
            TEST_NAME
        ).AndReturn(True)

        test_adapter.put_package(TEST_PACKAGE)

        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.put('/kpi/package/%s.json' % TEST_NAME, data=dict(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            authors=TEST_AUTHORS_INCLUSIVE_STR,
            license=TEST_LICENSE,
            humanName=TEST_HUMAN_NAME,
            name=TEST_NAME,
            version=TEST_VERSION
        ))

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertTrue(json_result['success'])

    def test_delete_package_fail_uac(self):
        self.mox.StubOutWithMock(util, 'check_permissions')
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)

        util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            TEST_PASSWORD,
            TEST_NAME
        ).AndReturn(False)

        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.post(
            '/kpi/package/%s.json/delete' % TEST_NAME,
            data=dict(
                username=TEST_USERNAME,
                password=TEST_PASSWORD
            )
        )

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertFalse(json_result['success'])

    def test_delete_package_success(self):
        self.mox.StubOutWithMock(util, 'check_permissions')
        test_adapter = self.mox.CreateMock(db_service.DBAdapter)

        util.check_permissions(
            test_adapter,
            TEST_USERNAME,
            TEST_PASSWORD,
            TEST_NAME
        ).AndReturn(True)

        test_adapter.delete_package(TEST_NAME)

        self.mox.ReplayAll()

        kpiserver.db_adapter = test_adapter

        response = self.app.post(
            '/kpi/package/%s.json/delete' % TEST_NAME,
            data=dict(
                username=TEST_USERNAME,
                password=TEST_PASSWORD
            )
        )

        self.assertEqual(response.status_code, 200)
        json_result = json.loads(response.data)
        self.assertTrue(json_result['success'])


if __name__ == '__main__':
    unittest.main()
