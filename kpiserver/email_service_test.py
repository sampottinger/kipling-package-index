"""Tests for convienence functions for the Kipling Package Index server.

@author: Sam Pottinger (samnsparky)
@license: GNU GPL v3
"""

import unittest

import mox

import email_service

TEST_API_KEY = 'apikey'
EMAIL_FROM_ADDRESS = 'EMAIL_FROM_ADDRESS'
EMAIL_FROM_NAME = 'EMAIL_FROM_NAME'
TEST_USERNAME = 'username'
TEST_PASSWORD = 'password'
TEST_EMAIL = 'test@example.com'


class MockApplication:

    def __init__(self, config):
        self.config = config


class EmailServiceTests(mox.MoxTestBase):

    def test_send_password_email_with_password(self):
        test_adapter = self.mox.CreateMock(email_service.MandrillServiceAdapter)

        test_application = MockApplication({
            'MAIL_API_KEY': TEST_API_KEY,
            'EMAIL_FROM_ADDRESS': EMAIL_FROM_ADDRESS,
            'EMAIL_FROM_NAME': EMAIL_FROM_NAME
        })

        self.mox.StubOutWithMock(email_service, 'get_client')
        email_service.get_client(test_application).AndReturn(test_adapter)

        message_text = email_service.PASSWORD_EMAIL_TEMPLATE % (
            TEST_USERNAME,
            TEST_PASSWORD
        )

        message = {
            'auto_html': True,
            'from_email': EMAIL_FROM_ADDRESS,
            'from_name': EMAIL_FROM_NAME,
            'subject': 'Your Kipling Package Index Account',
            'text': message_text,
            'to': [{'email': TEST_EMAIL, 'name': TEST_USERNAME, 'type': 'to'}]
        }
        test_adapter.send(message)
        
        self.mox.ReplayAll()

        email_service.send_password_email(
            test_application,
            TEST_EMAIL,
            TEST_USERNAME,
            TEST_PASSWORD
        )

    def test_send_password_email_no_password(self):
        test_adapter = self.mox.CreateMock(email_service.MandrillServiceAdapter)

        test_application = MockApplication({
            'MAIL_API_KEY': TEST_API_KEY,
            'EMAIL_FROM_ADDRESS': EMAIL_FROM_ADDRESS,
            'EMAIL_FROM_NAME': EMAIL_FROM_NAME
        })

        self.mox.StubOutWithMock(email_service, 'get_client')
        email_service.get_client(test_application).AndReturn(test_adapter)

        message_text = email_service.NO_PASSWORD_EMAIL_TEMPLATE % TEST_USERNAME

        message = {
            'auto_html': True,
            'from_email': EMAIL_FROM_ADDRESS,
            'from_name': EMAIL_FROM_NAME,
            'subject': 'Your Kipling Package Index Account',
            'text': message_text,
            'to': [{'email': TEST_EMAIL, 'name': TEST_USERNAME, 'type': 'to'}]
        }
        test_adapter.send(message)
        
        self.mox.ReplayAll()

        email_service.send_password_email(
            test_application,
            TEST_EMAIL,
            TEST_USERNAME
        )


if __name__ == '__main__':
    unittest.main()
