import unicodedata
import re
import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from urlparse import urlparse, parse_qs

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(80))
    has_image = db.Column(db.Boolean,default=0)
    image_md5 = db.Column(db.String(32))
    confirmed = db.Column(db.Boolean)

    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    bio = db.Column(db.Text())

    social_twitter = db.Column(db.String(255))
    social_facebook = db.Column(db.String(255))
    social_github = db.Column(db.String(255))

    def __init(self):
        self.has_image = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @property
    def display_name(self):
        if self.first_name:
            return (self.first_name + " " + self.last_name).strip()
        else:
            return self.username

    def get_image_path(self):
        folder = 'users-%s' % self.id
        image_filename = folder + '/avatar.jpg'
        return image_filename

    def __repr__(self):
        return '<User %r>' % (self.username)

class Admin(db.Model):
    __tablename__ = 'admins'
    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(80))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<Admin %r>' % (self.email)

class Presentation(db.Model):
    __tablename__ = 'presentations'
    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}

    id = db.Column(db.Integer, primary_key=True)
    added = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('presentations', lazy='dynamic'))

    finished = db.Column(db.Boolean,default=0)
    published = db.Column(db.Boolean,default=0)
    title = db.Column(db.String(250))
    url = db.Column(db.String(250))
    abstract = db.Column(db.Text())
    video = db.Column(db.String(255))

    slides = db.relationship('Slide', backref='presentation', lazy='dynamic')
    events = db.relationship('Event', backref='presentation', lazy='dynamic')
    links  = db.relationship('Link', backref='presentation', lazy='dynamic')

    def __init__(self, user_id):
        self.user_id = user_id

    def set_title(self, title):
        self.title = title

    def remove_slides(self):
        self.slides = []

    def add_slide(self, slide_nr, html):
        slide = Slide(self.id, slide_nr, html)
        self.slides.append(slide)
        return slide

    def first_slide(self):
        return Slide.query.filter_by(presentation_id=self.id, slide_nr=1).first()

    def add_event(self, event):
        self.events.append(event)
        return event

    def last_event(self):
        return Event.query.filter_by(presentation_id=self.id).order_by(db.desc(Event.presented)).first()

    def add_link(self, link):
        self.links.append(link)
        return link

    def get_id(self):
        return self.id

    def is_finished(self):
        return self.finished

    def set_finished(self):
        self.finished = True

    def get_url(self):
        return self.url

    def get_user_id(self):
        return self.user_id

    def get_pdf_path(self):
        folder = 'slides-%s' % self.id
        pdf_filename = folder + '/slides.pdf'
        return pdf_filename

    def is_video(self):
        if self.video is None:
            return False

        return self._get_video_id(self.video) is not None

    def get_video_url(self):
        video_id = self._get_video_id(self.video)

        return "http://www.youtube.com/embed/%s" % video_id

    def _get_video_id(self, value):
        query = urlparse(value)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        # fail?
        return None

    @db.validates('title')
    def _set_title(self, key, value):
        self.url = self._slugify(value)
        return value

    def _slugify(self, value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        """
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
        return re.sub('[-\s]+', '-', value)

    def __repr__(self):
        return '<Presentation %r>' % (self.id)

class Slide(db.Model):
    __tablename__ = 'slides'
    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}

    id = db.Column(db.Integer, primary_key=True)
    slide_nr = db.Column(db.Integer)
    html = db.Column(db.Text)
    image_md5 = db.Column(db.String(32))
    thumbnail_md5 = db.Column(db.String(32))

    presentation_id = db.Column(db.Integer, db.ForeignKey('presentations.id'))

    def __init__(self, presentation_id, slide_nr, html):
        self.presentation_id = presentation_id
        self.slide_nr = slide_nr
        self.html = html

    def get_slide_nr(self):
        return self.slide_nr

    def get_html(self):
        return self.html

    def get_image_path(self):
        folder = 'slides-%s' % self.presentation_id
        slide_filename = folder + '/%s.jpg' % self.slide_nr
        return slide_filename

    def get_thumbnail_path(self):
        folder = 'slides-%s' % self.presentation_id
        slide_filename = folder + '/%s-thumbnail.jpg' % self.slide_nr
        return slide_filename

class Event(db.Model):
    __tablename__ = 'events'
    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}

    id = db.Column(db.Integer, primary_key=True)
    presented = db.Column(db.Date, default=datetime.datetime.utcnow().date)
    location = db.Column(db.String(250))
    title = db.Column(db.String(250))

    presentation_id = db.Column(db.Integer, db.ForeignKey('presentations.id'))

class Link(db.Model):
    __tablename__ = 'links'
    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}

    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(250))
    title = db.Column(db.String(250))

    presentation_id = db.Column(db.Integer, db.ForeignKey('presentations.id'))

class Page(db.Model):
    __tablename__ = 'pages'
    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(250))
    title = db.Column(db.String(250))
    content = db.Column(db.Text())

    def __repr__(self):
        return '<Page %r>' % (self.id)