"""Tests for service to accept file uploads to the package index.

@author: Sam Pottinger
@license: GNU GPL v3
"""

import base64
import unittest

import mox

import file_store_service


class TestApplication:
    def __init__(self, config):
        self.config = config


class FileStoreServiceTests(mox.MoxTestBase):

    def test_create_file_upload_url(self):
        self.mox.StubOutWithMock(base64, 'encodestring')
        base64.encodestring(mox.IsA(basestring)).AndReturn('encoded')
        self.mox.ReplayAll()

        test_application = TestApplication({
            'UPLOADS_BUCKET_NAME': 'bucket_name',
            'S3_SECRET_KEY': 'test secret',
            'S3_ACCESS_KEY': 'access_key'
        })

        result = file_store_service.create_file_upload_url(
            test_application,
            'package'
        )

        self.assertTrue('https://bucket_name.s3.amazonaws.com' in result)
        self.assertTrue('/package.zip?AWSAccessKeyId=access_key' in result)
        self.assertTrue('&Signature=encoded' in result)


if __name__ == '__main__':
    unittest.main()
