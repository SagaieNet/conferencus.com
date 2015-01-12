from flask import Blueprint
from flask import redirect, request, abort
from flask import render_template, flash, redirect, url_for

from forms import UserForm

from ..models import db, User

bp = Blueprint('users', __name__)

@bp.route("/", defaults={'page': 1})
@bp.route('/<int:page>')
def index(page):
    users = User.query.order_by(db.desc(User.id)).paginate(page, 100)
    return render_template("users_index.html", users=users)

@bp.route('/edit/<id>', methods = ['GET', 'POST'])
def edit(id):
    user = User.query.get_or_404(id)

    form = UserForm(user)
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash("User saved.")
        return redirect(url_for("users.index"))
    return render_template("users_edit.html", form=form, user=user)

@bp.route('/delete/<id>', methods = ['GET'])
def delete(id):
    user = User.query.get_or_404(id)

    db.session.delete(user)
    db.session.commit()
    flash("User deleted.")
    return redirect(url_for("users.index"))