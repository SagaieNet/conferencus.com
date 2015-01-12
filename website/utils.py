from s3 import bucket
from boto.s3.key import Key

from flask import Response, current_app, render_template
from time import time

import subprocess

from StringIO import StringIO
from PIL import Image, ImageOps

from flask.ext.mail import Message

import rfc822

def get_modified(path):
    k = bucket.get_key(path)
    return k.etag.strip('"').strip("'"), int(rfc822.mktime_tz(rfc822.parsedate_tz(k.last_modified)))

def get_file(path):
    k = Key(bucket)
    k.key = path
    return k.get_contents_as_string()

def upload_file(key, data):
    k = Key(bucket)
    k.key = key
    k.set_contents_from_string(data)
    return k.md5

def pdfinfo(infile):
    """
    Wraps command line utility pdfinfo to extract the PDF meta information.
    Returns metainfo in a dictionary.
    sudo apt-get install poppler-utils

    This function parses the text output that looks like this:
        Title:          PUBLIC MEETING AGENDA
        Author:         Customer Support
        Creator:        Microsoft Word 2010
        Producer:       Microsoft Word 2010
        CreationDate:   Thu Dec 20 14:44:56 2012
        ModDate:        Thu Dec 20 14:44:56 2012
        Tagged:         yes
        Pages:          2
        Encrypted:      no
        Page size:      612 x 792 pts (letter)
        File size:      104739 bytes
        Optimized:      no
        PDF version:    1.5
    """
    import os.path as osp

    cmd = '/usr/bin/pdfinfo'
    if not osp.exists(cmd):
        raise RuntimeError('System command not found: %s' % cmd)

    if not osp.exists(infile):
        raise RuntimeError('Provided input file not found: %s' % infile)

    def _extract(row):
        """Extracts the right hand value from a : delimited row"""
        return row.split(':', 1)[1].strip()

    output = {}

    labels = ['Title', 'Author', 'Creator', 'Producer', 'CreationDate',
              'ModDate', 'Tagged', 'Pages', 'Encrypted', 'Page size',
              'File size', 'Optimized', 'PDF version']

    try:
        cmd_output = subprocess.check_output([cmd, infile], stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        return False

    for line in cmd_output.splitlines():
        for label in labels:
            if label in line:
                output[label] = _extract(line)

    return output


def resize_image(image, size):
    try:
        im = Image.open(StringIO(image))
    except IOError:
        return False

    # @TODO make a config
    thumb = ImageOps.fit(im, size, Image.ANTIALIAS)

    return image_to_string(thumb)

def image_to_string(image, format = 'JPEG'):
    result = StringIO()
    image.save(result, format)
    contents = result.getvalue()
    result.close()
    return contents

def send_mail(subject, recipient, template, **context):
    """Send an email via the Flask-Mail extension.

    :param subject: Email subject
    :param recipient: Email recipient
    :param template: The name of the email template
    :param context: The context to render the template with
    """
    app = current_app

    msg = Message(subject,
                  sender=app.config.get('MAIL_FROM'),
                  recipients=[recipient])

    ctx = ('email', template)
    msg.html = render_template('%s/%s.html' % ctx, **context)

    mail = current_app.extensions.get('mail')

    if not current_app.debug:
        mail.send(msg)
    else:
        print msg

def setup_logging(app):
    import os
    import logging
    from logging.handlers import RotatingFileHandler

    log_file = "/var/log/app/website.log"

    try:
        if os.path.isfile(log_file):
            with open(log_file) as file:
                pass
    except IOError as e:
        print "Unable to open file" #Does not exist OR no read permissions

    file_handler = RotatingFileHandler(log_file, 'a', maxBytes=1024 * 1024 * 100, backupCount=20)
    formatter = logging.Formatter('''
-----------------------------------------------------------------
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
    ''')
    file_handler.setFormatter(formatter)
    # file_handler.setLevel(logging.INFO)

    loggers = [app.logger, logging.getLogger('sqlalchemy'), logging.getLogger('werkzeug')]

    for logger in loggers:
        # logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)