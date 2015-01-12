from flask import Blueprint
from flask import redirect, request, abort
from flask import render_template, flash, redirect, url_for

from forms import PresentationForm

from ..tasks import process_slides
from ..models import db, Presentation

bp = Blueprint('slidedeck', __name__)

@bp.route("/", defaults={'page': 1})
@bp.route('/<int:page>')
def index(page):
    presentations = Presentation.query.order_by(db.desc(Presentation.id)).paginate(page, 100)
    return render_template("slidedeck_index.html", presentations=presentations)

@bp.route('/edit/<id>', methods = ['GET', 'POST'])
def edit(id):
    presentation = Presentation.query.get_or_404(id)

    form = PresentationForm(obj=presentation)
    if form.validate_on_submit():
        form.populate_obj(presentation)
        db.session.commit()
        flash("Presentation saved.")
        return redirect(url_for("slidedeck.index"))
    return render_template("slidedeck_edit.html", form=form, presentation=presentation)

@bp.route('/reprocess/<id>', methods = ['GET'])
def reprocess(id):
    presentation = Presentation.query.get_or_404(id)

    process_slides.delay(presentation.id)

    flash("Presentation reprocessing.")
    return redirect(url_for('slidedeck.index'))

@bp.route('/delete/<id>', methods = ['GET'])
def delete(id):
    presentation = Presentation.query.get_or_404(id)

    db.session.delete(presentation)
    db.session.commit()
    flash("Presentation deleted.")
    return redirect(url_for("slidedeck.index"))