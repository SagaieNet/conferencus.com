from flask import current_app

from itsdangerous import URLSafeTimedSerializer
from itsdangerous import BadSignature, SignatureExpired

import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

def get_serializer(name):
    app = current_app
    secret_key = app.config.get('SECRET_KEY')
    salt = app.config.get('SECURITY_%s_SALT' % name.upper())
    return URLSafeTimedSerializer(secret_key=secret_key, salt=salt)

def generate_confirmation_token(user):
    """Generates a unique confirmation token for the specified user.

    :param user: The user to work with
    """
    data = [str(user.id), md5(user.email)]
    serializer = get_serializer('password')
    return serializer.dumps(data)

def confirm_email_token_status(token):
    """Returns the expired status, invalid status, and user of a confirmation
    token. For example::

        expired, invalid, user = confirm_email_token_status('...')

    :param token: The confirmation token
    """
    return get_token_status(token, 3600)

def generate_reset_password_token(user):
    """Generates a unique reset password token for the specified user.

    :param user: The user to work with
    """
    data = [str(user.id), md5(user.password)]
    serializer = get_serializer('password')
    return serializer.dumps(data)

def reset_password_token_status(token):
    """Returns the expired status, invalid status, and user of a password reset
    token. For example::

        expired, invalid, user = reset_password_token_status('...')

    :param token: The password reset token
    """
    return get_token_status(token, 3600)

def get_token_status(token, max_age=None):
    """Get the status of a token.

    :param token: The token to check
    :param max_age: The seconds token is valid form
    """
    serializer = get_serializer('password')
    user, data = None, None
    expired, invalid = False, False

    try:
        data = serializer.loads(token, max_age=max_age)
    except SignatureExpired:
        d, data = serializer.loads_unsafe(token)
        expired = True
    except (BadSignature, TypeError, ValueError):
        invalid = True

    if data:
        user = data[0]

    expired = expired and (user is not None)
    return expired, invalid, user

def md5(data):
    return hashlib.md5(encode_string(data)).hexdigest()

def encode_string(string):
    """Encodes a string to bytes, if it isn't already.

    :param string: The string to encode"""

    string = string.encode('utf-8')
    return string