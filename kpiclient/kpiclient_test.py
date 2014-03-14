"""Automated tests for the Kipling Package Index command line tool.

@author: Sam Pottinger (samnsparky)
@license: GNU GPL v3
"""

import unittest

import mox
import requests

import kpiclient


class KPIClientTests(mox.MoxTestBase):

    def test_generate_error(self):
        test_error = 'error message'
        error_info = kpiclient.generate_error(test_error).json()
        self.assertEqual(error_info['success'], False)
        self.assertEqual(error_info['message'], test_error)

    def test_add_user_info(self):
        user_info = kpiclient.UserInfo('user', 'pass')
        target_dict = {'test': 1}
        kpiclient.add_user_info(user_info, target_dict)
        self.assertEqual(target_dict['test'], 1)
        self.assertEqual(target_dict['username'], 'user')
        self.assertEqual(target_dict['password'], 'pass')

    def test_parse_response(self):
        response = kpiclient.FakeResponse({'test': 1})
        parsed_response = kpiclient.parse_response(response)
        self.assertEqual(parsed_response['test'], 1)

    def test_deploy_new(self):
        user_info = kpiclient.UserInfo('user', 'pass')
        test_json_info = {
            'name': 'analog_inputs',
            'humanName': 'Analog Inputs',
            'version': '0.0.1',
            'authors': ['user1', 'user2'],
            'license': 'MIT'
        }
        upload_spec = {'test1':1, 'test2': 2}
        first_response = {
            'success': True,
            'upload_url': 'remote_url',
            'upload_spec': upload_spec
        }
        second_response = {'test3': 3}

        self.mox.StubOutWithMock(kpiclient, 'get_module_json')
        self.mox.StubOutWithMock(requests, 'post')
        self.mox.StubOutWithMock(requests, 'put')
        self.mox.StubOutWithMock(kpiclient, 'upload_zip_file')

        kpiclient.get_module_json('module_path').AndReturn(test_json_info)
        requests.post(
            kpiclient.PACKAGES_URL,
            data={
                'username': 'user',
                'password': 'pass',
                'name': 'analog_inputs',
                'humanName': 'Analog Inputs',
                'version': '0.0.1',
                'authors': ['user1', 'user2'],
                'license': 'MIT'
            }
        ).AndReturn(kpiclient.FakeResponse(first_response))
        kpiclient.upload_zip_file(
            'zip_path',
            'remote_url',
            upload_spec
        ).AndReturn(kpiclient.FakeResponse(second_response))

        self.mox.ReplayAll()

        response = kpiclient.create(
            user_info,
            'package',
            'module_path',
            'zip_path'
        )
        self.assertEqual(response.json(), first_response)

    def test_deploy_new_missing(self):
        user_info = kpiclient.UserInfo('user', 'pass')
        test_json_info = {
            'name': 'analog_inputs',
            'humanName': 'Analog Inputs',
            'version': '0.0.1',
            'license': 'MIT'
        }
        expected_response = {'test3': 3}

        self.mox.StubOutWithMock(kpiclient, 'get_module_json')
        self.mox.StubOutWithMock(requests, 'post')
        self.mox.StubOutWithMock(requests, 'put')
        self.mox.StubOutWithMock(kpiclient, 'upload_zip_file')

        kpiclient.get_module_json('module_path').AndReturn(test_json_info)

        self.mox.ReplayAll()

        response = kpiclient.deploy(
            user_info,
            'package',
            'module_path',
            'zip_path',
            True
        )
        self.assertEqual(response.json()['success'], False)

    def test_deploy_new_bad_json(self):
        user_info = kpiclient.UserInfo('user', 'pass')
        test_json_info = {
            'name': 'analog_inputs',
            'humanName': 'Analog Inputs',
            'version': '0.0.1',
            'authors': ['user1', 'user2'],
            'license': 'MIT'
        }
        upload_spec = {'test1':1, 'test2': 2}
        first_response = {
            'success': True,
            'upload_url': 'remote_url',
            'upload_spec': upload_spec
        }
        second_response = {'test3': 3}

        self.mox.StubOutWithMock(kpiclient, 'get_module_json')
        self.mox.StubOutWithMock(requests, 'post')
        self.mox.StubOutWithMock(requests, 'put')
        self.mox.StubOutWithMock(kpiclient, 'upload_zip_file')

        kpiclient.get_module_json('module_path').AndReturn(test_json_info)
        requests.post(
            kpiclient.PACKAGES_URL,
            data={
                'username': 'user',
                'password': 'pass',
                'name': 'analog_inputs',
                'humanName': 'Analog Inputs',
                'version': '0.0.1',
                'authors': ['user1', 'user2'],
                'license': 'MIT'
            }
        ).AndReturn(kpiclient.FakeResponse(first_response))
        kpiclient.upload_zip_file(
            'zip_path',
            'remote_url',
            upload_spec
        ).AndReturn(kpiclient.FakeResponse(second_response))

        self.mox.ReplayAll()

        response = kpiclient.deploy(
            user_info,
            'package',
            'module_path',
            'zip_path',
            True
        )
        self.assertEqual(response.json(), first_response)

    def test_deploy_existing(self):
        user_info = kpiclient.UserInfo('user', 'pass')
        test_json_info = {
            'name': 'analog_inputs',
            'humanName': 'Analog Inputs',
            'version': '0.0.1',
            'authors': ['user1', 'user2'],
            'license': 'MIT'
        }
        upload_spec = {'test1':1, 'test2': 2}
        first_response = {
            'success': True,
            'upload_url': 'remote_url',
            'upload_spec': upload_spec
        }
        second_response = {'test3': 3}

        self.mox.StubOutWithMock(kpiclient, 'get_module_json')
        self.mox.StubOutWithMock(requests, 'post')
        self.mox.StubOutWithMock(requests, 'put')
        self.mox.StubOutWithMock(kpiclient, 'upload_zip_file')

        kpiclient.get_module_json('module_path').AndReturn(test_json_info)
        requests.put(
            kpiclient.PACKAGE_URL % 'analog_inputs',
            data={
                'username': 'user',
                'password': 'pass',
                'name': 'analog_inputs',
                'humanName': 'Analog Inputs',
                'version': '0.0.1',
                'authors': ['user1', 'user2'],
                'license': 'MIT'
            }
        ).AndReturn(kpiclient.FakeResponse(first_response))
        kpiclient.upload_zip_file(
            'zip_path',
            'remote_url',
            upload_spec
        ).AndReturn(kpiclient.FakeResponse(second_response))

        self.mox.ReplayAll()

        response = kpiclient.update(
            user_info,
            'package',
            'module_path',
            'zip_path'
        )
        self.assertEqual(response.json(), first_response)

    def test_read(self):
        package_name = 'test_module'
        test_response = kpiclient.FakeResponse({
            'success': True,
            'record': 'record'
        })

        self.mox.StubOutWithMock(requests, 'get')
        self.mox.StubOutWithMock(kpiclient, 'internal_print_table')

        requests.get(
            kpiclient.PACKAGE_URL % package_name
        ).AndReturn(test_response)
        kpiclient.internal_print_table('record')
        self.mox.ReplayAll()

        kpiclient.read(package_name)

    def test_delete(self):
        package_name = 'test_module'
        test_response = kpiclient.FakeResponse({
            'success': True
        })
        test_user = kpiclient.UserInfo('user', 'pass')

        self.mox.StubOutWithMock(requests, 'delete')

        requests.delete(
            kpiclient.PACKAGE_URL % package_name,
            data={'username': 'user', 'password': 'pass', 'name': package_name}
        ).AndReturn(test_response)
        self.mox.ReplayAll()

        kpiclient.delete(test_user, package_name)

    def test_useradd(self):
        self.mox.StubOutWithMock(requests, 'post')
        requests.post(kpiclient.USERS_URL, data={
            'username': 'testuser',
            'email': 'test@example.com'
        })
        self.mox.ReplayAll()

        kpiclient.useradd('testuser', 'test@example.com')

    def test_passwd(self):
        self.mox.StubOutWithMock(requests, 'post')
        requests.post(kpiclient.USER_URL % 'testuser', data={
            'username': 'testuser',
            'old_password': 'old',
            'new_password': 'new'
        })
        self.mox.ReplayAll()

        kpiclient.passwd('testuser', 'old', 'new', 'new')

    def test_passwd_mismatch(self):
        self.mox.StubOutWithMock(requests, 'post')
        self.mox.ReplayAll()

        result = kpiclient.passwd('testuser', 'old', 'new', 'newother').json()
        self.assertFalse(result['success'])


if __name__ == '__main__':
    unittest.main()
