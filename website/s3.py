from boto.s3.connection import S3Connection
import os
from flask.config import Config

env = os.environ.get('ENV', 'dev')
config = Config('')
config.from_object('website.settings.%sConfig' % env.capitalize())

s3 = S3Connection(config['AWS_ACCESS'], config['AWS_SECRET'])
bucket = s3.lookup(config['S3_BUCKET'])
