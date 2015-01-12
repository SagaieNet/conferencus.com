import os
from flask import Flask, render_template, request, redirect, url_for, abort, session
from flask.ext.login import LoginManager
from flask.ext.babel import Babel
from flask.ext.assets import Environment
from flask.ext.mail import Mail
from ..models import db, User, Presentation
from ..utils import setup_logging

import re
from jinja2 import evalcontextfilter, Markup, escape

app = Flask(__name__)

env = os.environ.get('ENV', 'dev')
app.config.from_object('website.settings.%sConfig' % env.capitalize())
app.config['ENV'] = env

if not app.debug:
    setup_logging(app)

babel = Babel(app)
db.init_app(app)
assets = Environment(app)
mail = Mail(app)

lm = LoginManager()
lm.setup_app(app)
lm.login_view = "user.login"

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

import user
app.register_blueprint(user.bp, url_prefix='/user')

import slidedeck
app.register_blueprint(slidedeck.bp, url_prefix='/talks')

import pages
app.register_blueprint(pages.bp)

@app.route("/")
def index():
    presentations = Presentation.query.filter_by(finished=True,published=True).order_by(db.desc(Presentation.id)).limit(8).all()
    return render_template('index.html', presentations=presentations)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

try:
    from wtforms.fields import HiddenField
except ImportError:
    def is_hidden_field_filter(field):
        raise RuntimeError('WTForms is not installed.')
else:
    def is_hidden_field_filter(field):
        return isinstance(field, HiddenField)

app.jinja_env.filters['bootstrap_is_hidden_field'] = is_hidden_field_filter

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page

    query_string = request.query_string

    if query_string:
        return url_for(request.endpoint, **args) + "?" + query_string
    else:
        return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

from werkzeug.urls import url_quote

@app.template_filter()
@evalcontextfilter
def urlquote(eval_ctx, value):
    result = url_quote(value)
    return result