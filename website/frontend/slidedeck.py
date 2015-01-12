from flask import Blueprint
from flask import redirect, request, abort
from flask import render_template, flash, redirect, url_for
from flask.ext.login import current_user, login_required

from forms import UploadForm, PresentationForm, EventForm, LinkForm

from ..utils import upload_file
from ..tasks import process_slides
from ..models import db, Slide, Presentation, Event, Link
from proxy import image_response

bp = Blueprint('slidedeck', __name__)

@bp.route("/", defaults={'page': 1})
@bp.route('/<int:page>')
def index(page):
    search = request.args.get('search')

    presentations = Presentation.query.filter_by(finished=True, published=True)

    if search:
        presentations = presentations.filter(Presentation.title.like("%" + search + "%") | Presentation.abstract.like("%" + search + "%"))

    presentations = presentations.order_by(db.desc(Presentation.id)).paginate(page, 20)
    return render_template("slidedeck_index.html", presentations=presentations, search=search)

@bp.route('/upload', methods = ['GET', 'POST'])
@login_required
def upload():
    user_id = current_user.get_id()
    form = UploadForm()
    if form.validate_on_submit():
        presentation = Presentation(user_id)
        form.populate_obj(presentation)

        if form.event.data:
            event = Event()
            event.title = form.event.data
            event.presented = form.presented.data
            event.location = form.location.data
            presentation.add_event(event)

        db.session.add(presentation)
        db.session.commit()

        upload_file(presentation.get_pdf_path(), form.slides_file.data.read())

        process_slides.delay(presentation.id)
        return redirect(url_for('user.profile', username=current_user.username))
    return render_template("slidedeck_upload.html", form=form)

@bp.route('/<url>-<int:id>', methods = ['GET'])
def watch(url, id):
    presentation = Presentation.query.get_or_404(id)

    # make sure url is up to date
    if presentation.get_url() != url:
        return redirect(url_for('slidedeck.watch', url=presentation.get_url(), id=presentation.get_id()))

    # if presentation is not finished processing:
    if not presentation.is_finished():
        return abort(404)

    # if presentation is not published
    if not presentation.published and current_user.get_id() != presentation.user_id:
        return abort(404)

    return render_template("slidedeck_presentation.html", presentation=presentation)

@bp.route('/<url>-<int:id>/edit', methods = ['GET', 'POST'])
@login_required
def edit(url, id):
    presentation = Presentation.query.get_or_404(id)

    if current_user.get_id() != presentation.user_id:
        return abort(404)

    form = PresentationForm(obj=presentation)

    # not finished talks and not confirmed talks cannot publish talks
    if not presentation.finished or not presentation.user.confirmed:
        del form.published

    if form.validate_on_submit():
        form.populate_obj(presentation)

        slides = form.slides_file.data
        if slides:
            upload_file(presentation.get_pdf_path(), slides.read())
            process_slides.delay(presentation.id)

        db.session.commit()
        flash("Presentation saved.")
        if not presentation.is_finished():
            return redirect(url_for('user.profile', username=current_user.username))
        else:
            return redirect(url_for('slidedeck.watch', url=presentation.get_url(), id=presentation.get_id()))

    events = presentation.events
    links = presentation.links

    return render_template("slidedeck_edit.html", form=form, presentation=presentation, events=events, links=links)

@bp.route('/<url>-<int:id>/delete', methods = ['GET'])
@login_required
def delete(url, id):
    presentation = Presentation.query.get_or_404(id)

    if current_user.get_id() != presentation.user_id:
        return abort(404)

    db.session.delete(presentation)
    db.session.commit()
    flash("Presentation deleted.")
    return redirect(url_for('user.profile', username=current_user.username))

@bp.route('/<url>-<int:id>/<int:slide_nr>.jpg', methods = ['GET'])
def slide(url, id, slide_nr):
    presentation = Presentation.query.get_or_404(id)

    # make sure url is up to date
    if presentation.get_url() != url:
        return redirect(url_for('slidedeck.slide', url=presentation.get_url(), id=presentation.get_id(), slide_nr=slide_nr))

    slide = Slide.query.filter_by(presentation_id=presentation.get_id(), slide_nr=slide_nr).first()

    if slide is None:
        return abort(404)

    return image_response(slide.get_image_path())

@bp.route('/<url>-<int:id>/thumbnail.jpg', methods = ['GET'])
def thumbnail(url, id):
    presentation = Presentation.query.get_or_404(id)

    # make sure url is up to date
    if presentation.get_url() != url:
        return redirect(url_for('slidedeck.thumbnail', url=presentation.get_url(), id=presentation.get_id()))

    slide = presentation.first_slide()

    if slide is None:
        return abort(404)

    return image_response(slide.get_thumbnail_path())

@bp.route('/<url>-<int:id>/events', methods = ['GET', 'POST'])
@login_required
def event_add(url, id):
    presentation = Presentation.query.get_or_404(id)

    if current_user.get_id() != presentation.user_id:
        return abort(404)

    form = EventForm()
    if form.validate_on_submit():
        event = Event()
        form.populate_obj(event)
        presentation.add_event(event)
        db.session.commit()
        flash("Event added.")
        return redirect(url_for('slidedeck.edit', id=presentation.id, url=presentation.url))
    return render_template("slidedeck_event_add.html", form=form)

@bp.route('/<url>-<int:id>/events/<int:event_id>', methods = ['GET', 'POST'])
@login_required
def event_edit(url, id, event_id):
    presentation = Presentation.query.get_or_404(id)

    if current_user.get_id() != presentation.user_id:
        return abort(404)

    event = Event.query.get_or_404(event_id)

    if event.presentation_id != presentation.id:
        return abort(404)

    form = EventForm(obj=event)
    if form.validate_on_submit():
        form.populate_obj(event)
        db.session.commit()
        flash("Event saved.")
        return redirect(url_for('slidedeck.edit', id=presentation.id, url=presentation.url))
    return render_template("slidedeck_event_edit.html", form=form)

@bp.route('/<url>-<int:id>/events/<int:event_id>/delete', methods = ['GET'])
@login_required
def event_delete(url, id, event_id):
    presentation = Presentation.query.get_or_404(id)

    if current_user.get_id() != presentation.user_id:
        return abort(404)

    event = Event.query.get_or_404(event_id)

    if event.presentation_id != presentation.id:
        return abort(404)

    db.session.delete(event)
    db.session.commit()
    flash("Event deleted.")
    return redirect(url_for('slidedeck.edit', id=presentation.id, url=presentation.url))

@bp.route('/<url>-<int:id>/links', methods = ['GET', 'POST'])
@login_required
def link_add(url, id):
    presentation = Presentation.query.get_or_404(id)

    if current_user.get_id() != presentation.user_id:
        return abort(404)

    form = LinkForm()
    if form.validate_on_submit():
        link = Link()
        form.populate_obj(link)
        presentation.add_link(link)
        db.session.commit()
        flash("Link added.")
        return redirect(url_for('slidedeck.edit', id=presentation.id, url=presentation.url))
    return render_template("slidedeck_link_add.html", form=form)

@bp.route('/<url>-<int:id>/links/<int:link_id>', methods = ['GET', 'POST'])
@login_required
def link_edit(url, id, link_id):
    presentation = Presentation.query.get_or_404(id)

    if current_user.get_id() != presentation.user_id:
        return abort(404)

    link = Link.query.get_or_404(link_id)

    if link.presentation_id != presentation.id:
        return abort(404)

    form = LinkForm(obj=link)
    if form.validate_on_submit():
        form.populate_obj(link)
        db.session.commit()
        flash("Link saved.")
        return redirect(url_for('slidedeck.edit', id=presentation.id, url=presentation.url))
    return render_template("slidedeck_link_edit.html", form=form)

@bp.route('/<url>-<int:id>/links/<int:link_id>/delete', methods = ['GET'])
@login_required
def link_delete(url, id, link_id):
    presentation = Presentation.query.get_or_404(id)

    if current_user.get_id() != presentation.user_id:
        return abort(404)

    link = Link.query.get_or_404(link_id)

    if link.presentation_id != presentation.id:
        return abort(404)

    db.session.delete(link)
    db.session.commit()
    flash("Link deleted.")
    return redirect(url_for('slidedeck.edit', id=presentation.id, url=presentation.url))