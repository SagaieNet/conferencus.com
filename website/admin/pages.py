from flask import Blueprint
from flask import redirect, request, abort
from flask import render_template, flash, redirect, url_for

from forms import PageForm

from ..models import db, Page

bp = Blueprint('pages', __name__)

@bp.route("/", defaults={'page': 1})
@bp.route('/<int:page>')
def index(page):
    pages = Page.query.order_by(db.desc(Page.id)).paginate(page, 100)
    return render_template("pages_index.html", pages=pages)

@bp.route('/add', methods = ['GET', 'POST'])
def add():
    page = Page()

    form = PageForm()
    if form.validate_on_submit():
        form.populate_obj(page)
        db.session.add(page)
        db.session.commit()
        flash("Page added.")
        return redirect(url_for("pages.index"))
    return render_template("pages_add.html", form=form)

@bp.route('/edit/<id>', methods = ['GET', 'POST'])
def edit(id):
    page = Page.query.get_or_404(id)

    form = PageForm(obj=page)
    if form.validate_on_submit():
        form.populate_obj(page)
        db.session.commit()
        flash("Page saved.")
        return redirect(url_for("pages.index"))
    return render_template("pages_edit.html", form=form, page=page)
