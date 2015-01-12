from flask import Flask
from celery import Celery
from celery.utils.log import get_task_logger

from models import db, Presentation, Slide

from utils import resize_image, upload_file, get_file

import os, tempfile
import subprocess
import json

base = os.path.realpath(os.path.dirname(__file__) + "/../")
script = "xvfb-run --auto-servernum slimerjs " + base + "/convert/render.js %s %s"

def create_celery_app():
    app = Flask(__name__)

    env = os.environ.get('ENV', 'dev')
    app.config.from_object('website.settings.%sConfig' % env.capitalize())
    app.config['ENV'] = env

    db.app = app
    db.init_app(app)

    celery = Celery('slides.tasks', broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)

    return celery

celery = create_celery_app()

logger = get_task_logger(__name__)

@celery.task()
def process_slides(id):
    presentation = Presentation.query.filter_by(id=id).first()

    if presentation is None:
        raise Exception("Processed invalid presentation %s" % id)

    slidedeck_id = presentation.get_id()

    pdf_contents = get_file(presentation.get_pdf_path())

    _, slides_file = tempfile.mkstemp()
    pdf = open(slides_file,"wb")
    pdf.write(pdf_contents)
    pdf.close()
    os.chmod(slides_file, 0666)

    _, output_file = tempfile.mkstemp()
    os.chmod(output_file, 0666)
    run_command = script % (slides_file, output_file)

    logger.info("Running %s" % run_command)

    # runs the conversation and waits till it finishes
    for line in runProcess(run_command):
        logger.info(line)

    # reset slides
    presentation.remove_slides()

    slide_nr = 1
    with open(output_file) as f:
        for page_ in f.readlines():
            try:
                page = json.loads(page_)

                html = page['html']
                image = page['slide'].replace('data:image/jpeg;base64,', '').decode('base64')

                slide = presentation.add_slide(slide_nr, html)

                image_md5, thumbnail_md5 = upload_images(slide, image)

                slide.image_md5 = image_md5
                slide.thumbnail_md5 = thumbnail_md5

                slide_nr += 1
            except ValueError:
                print page_

    # delete temp files
    os.remove(slides_file)
    os.remove(output_file)

    # this presentation has finished processing
    presentation.set_finished()

    try_commit()

    if slide_nr > 1:
        return True
    else:
        return False

def try_commit():
    try:
        db.session.commit()
        db.session.expunge_all()
    except:
        db.session.rollback()
        raise

def upload_images(slide, image):
    image_md5 = upload_file(slide.get_image_path(), image)

    # @TODO make a config
    size = (320, 180)
    thumb = resize_image(image, size)

    thumbnail_md5 = upload_file(slide.get_thumbnail_path(), thumb)

    return image_md5, thumbnail_md5

def runProcess(command):
    p = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE)
    while(True):
        retcode = p.poll() #returns None while subprocess is running
        line = p.stdout.readline()
        yield line
        if(retcode is not None):
            break