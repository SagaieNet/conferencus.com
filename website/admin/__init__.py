import os
from flask import Flask, render_template, request, redirect, url_for, abort, flash
from flask.ext.login import LoginManager, current_user, login_required, logout_user, login_user
from flask.ext.babel import Babel
from flask.ext.assets import Environment
from ..models import db, Admin
from forms import LoginForm

app = Flask(__name__)

env = os.environ.get('ENV', 'dev')
app.config.from_object('website.settings.%sConfig' % env.capitalize())
app.config['ENV'] = env

babel = Babel(app)
db.init_app(app)
assets = Environment(app)

lm = LoginManager()
lm.setup_app(app)

@lm.user_loader
def load_user(id):
    return Admin.query.get(int(id))

import slidedeck
app.register_blueprint(slidedeck.bp, url_prefix='/talks')

import users
app.register_blueprint(users.bp, url_prefix='/users')

import pages
app.register_blueprint(pages.bp, url_prefix='/pages')

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user, remember = form.remember_me.data)
        flash("Logged in successfully.")
        return redirect(request.args.get("next") or url_for("index"))
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logged out.")
    return redirect(url_for("index"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.before_request
def before_request():
    if not current_user.is_authenticated() and request.endpoint != 'login' and request.endpoint.find('static') == -1:
        return redirect(url_for('login'))

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
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page
