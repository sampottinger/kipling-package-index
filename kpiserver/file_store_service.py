import base64
import hashlib
import hmac
import time
import urllib

ZIP_MIME_TYPE = 'application/zip'


def create_file_upload_url(application, package_name):
    """Create a signed URL where the contents of a resource can be uploaded.

    @param package_name: The name of the package that a url is being generated
        for.
    @type resource: str
    @return: Temporary URL that will accept a PUT with resource content.
    @rtype: str
    """
    object_name = package_name + '.zip'
    mime_type = ZIP_MIME_TYPE

    expires = int(time.time()+10)
    amz_headers = "x-amz-acl:public-read"

    put_request = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (
        mime_type,
        expires,
        amz_headers,
        application.config['UPLOADS_BUCKET_NAME'],
        object_name
    )

    signature = base64.encodestring(hmac.new(
        application.config['S3_SECRET_KEY'],
        put_request,
        hashlib.sha1
    ).digest())
    signature = urllib.quote_plus(signature.strip())

    url = 'https://%s.s3.amazonaws.com/%s' % (
        application.config['UPLOADS_BUCKET_NAME'],
        object_name
    )

    signed_req_url = '%s?AWSAccessKeyId=%s&Expires=%d&Signature=%s' % (
        url,
        application.config['S3_ACCESS_KEY'],
        expires,
        signature
    )
    return signed_req_url
