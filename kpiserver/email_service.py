import mandrill

PASSWORD_EMAIL_TEMPLATE = '''Hello %s,

Your password for the Kipling Package Index has been changed to: %s.

Cheers,
LabJack
'''

NO_PASSWORD_EMAIL_TEMPLATE = '''Hello %s,

Just wanted to confirm that you changed your password for your Kipling Package
Index account.

Cheers,
LabJack
'''


class EmailServiceAdapter:
    """Interface for a service for sending emails to users."""

    def send(self, message):
        """Send a message to a user.

        @param message: Information about the message to send. Should be a
            dictionary with fields:
             - auto_html: (boolean) Should HTML body be generated from plaintext
             - from_email: (string) The email address that the message should be
                sent from
             - from_name: (string) The human friendly name of the person who
                the message should be reported as having come from.
             - subject: (string) The human friendly subject line for the
                message.
             - text: (string) The text body of the email.
             - to: (list) list of recipients of form
                [{'email': , 'name': , 'type': 'to'}]
        @type message: dict
        """
        raise NotImplementedError()


class MandrillServiceAdapter(EmailServiceAdapter):
    """Implementation of the EmailServiceAdapter for Mandrill."""

    def __init__(self, native_client):
        """Create a new adapter around a native Mandrill client.

        @param native_client: The client to adapt.
        @type native_client: mandrill.Mandrill
        """
        self.native_client = native_client

    def send(self, message):
        self.native_client.messages.send(message=message, async=False)


def get_client(application):
    """Get the email client for the service specified by configuration

    @param application: The application that has the configuration values
        necessary for interacting with the mailing service.
    @type application: flask.Flask
    @return: Implementor of EmailServiceAdapter
    @type: EmailServiceAdapter
    """
    return MandrillAdapter(mandrill.Mandrill(api_key))


def send_password_email(application, email, username, password=None):
    """Send a user an email alert indicating that their password changed.

    Send a user an email alert indicating that their password changed. This
    message will include their plaintext password if the password keyword is
    not None.

    @param application: The application that has the configuration values
        necessary for interacting with the mailing service.
    @type application: flask.Flask
    @param email: The email address of the user whose password changed.
    @type email: str
    @param username: The username of the user whose password changed.
    @type username: str
    @keyword password: The plaintext password for the user. Will be included
        in the email if this is not None. Defaults to None.
    @type password: str
    """
    client = get_client(application)

    if password:
        message_text = PASSWORD_EMAIL_TEMPLATE % (username, password)
    else:
        message_text = NO_PASSWORD_EMAIL_TEMPLATE % username

    message = {
        'auto_html': True,
        'from_email': application.config['EMAIL_FROM_ADDRESS'],
        'from_name': application.config['EMAIL_FROM_NAME'],
        'subject': 'Your Kipling Package Index Account',
        'text': message_text,
        'to': [{'email': email, 'name': username, 'type': 'to'}]
    }

    client.send(message)
