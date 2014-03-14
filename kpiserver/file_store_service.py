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

    # Creating a signed URL where the user can post their file directly to S3,
    # avoiding costs of transmission and request timeout limits. These signed
    # URLs are strongly encouraged to have an expiration if POST.
    expires = int(time.time()+10)

    # Amazon requires an access control level for each of its files. These
    # uploads should be read only by the public.
    amz_headers = "x-amz-acl:public-read"

    # We have to construct this by hand as opposed to using somebody like
    # requestify because we have to hash it and sign it with our Amazon
    # secret key.
    put_request = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (
        mime_type,
        expires,
        amz_headers,
        application.config['UPLOADS_BUCKET_NAME'],
        object_name
    )

    # Signed with secret key without revealing that secret key to the world.
    signature = base64.encodestring(hmac.new(
        application.config['S3_SECRET_KEY'],
        put_request,
        hashlib.sha1
    ).digest())
    signature = urllib.quote_plus(signature.strip())

    # Build and return final URL
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
