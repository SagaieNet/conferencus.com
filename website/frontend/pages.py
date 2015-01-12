from flask import Blueprint
from flask import redirect, request
from flask import render_template, flash, redirect, url_for, abort

from ..models import db, Page

bp = Blueprint('pages', __name__)

@bp.route("/about")
def about():
    return render_page("about")

@bp.route("/copyright")
def copyright():
    return render_page("copyright")

@bp.route("/contact")
def contact():
    return render_page("contact")

def render_page(name):
    page = Page.query.filter_by(url=name).first()
    return render_template("pages_page.html", page=page)