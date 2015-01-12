from flask import Blueprint
from flask import redirect, request
from flask import current_app, render_template, flash, redirect, url_for, abort
from flask.ext.login import login_user, logout_user, current_user, login_required

from forms import LoginForm, RegisterForm, UserForm, PasswordForm, PasswordResetForm

from ..models import db, User, Presentation
from ..utils import upload_file, resize_image, send_mail
from security import *
from proxy import image_response

bp = Blueprint('user', __name__)

@bp.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated():
        return redirect(url_for('index'))
    user = User()
    form = RegisterForm()
    if form.validate_on_submit():
        form.populate_obj(user)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        token = generate_confirmation_token(user)
        confirmation_link = url_for('user.confirm_email', token=token, _external=True)

        send_mail('Welcome!', user.email, 'confirmation_instructions', user=user, confirmation_link=confirmation_link)

        login_user(user, remember = True)
        flash("Registered successfully.")
        return redirect(request.args.get("next") or url_for("user.edit"))
    return render_template("user_register.html", form=form)

@bp.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user, remember = form.remember_me.data)
        return redirect(request.args.get("next") or url_for("index"))
    return render_template("user_login.html", form=form)

@bp.route('/forgot', methods = ['GET', 'POST'])
def password_reset():
    if current_user.is_authenticated():
        return redirect(url_for('index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = form.user
        token = generate_reset_password_token(user)
        reset_link = url_for('user.password', token=token, _external=True)

        send_mail('Password Reset', user.email, 'password_reset_instructions', user=user, reset_link=reset_link)

        flash("Password reset link has been emailed.")
        return redirect(url_for("user.login"))
    return render_template("user_password_reset.html", form=form)

@bp.route("/settings", methods = ['GET', 'POST'])
@login_required
def edit():
    user = User.query.get_or_404(current_user.get_id())
    form = UserForm(user)
    if form.validate_on_submit():
        form.populate_obj(user)

        avatar = form.avatar.data
        if avatar:
            _avatar = resize_image(avatar.read(), (500, 500))
            md5 = upload_file(user.get_image_path(), _avatar)
            user.has_image = True
            user.image_md5 = md5

        db.session.commit()

        flash("Profile updated.")
        return redirect(url_for("user.profile", username = user.username))
    return render_template("user_edit.html", form=form)

@bp.route("/settings/password", methods = ['GET', 'POST'])
def password():
    token = request.args.get("token")
    if token:
        expired, invalid, user_id = reset_password_token_status(token)

        if invalid or expired:
            flash("Invalid token.")
            return redirect(url_for('user.password_reset'))

        user = User.query.get_or_404(user_id)
    else:
        if not current_user.is_authenticated():
            return current_app.login_manager.unauthorized()

        user = User.query.get_or_404(current_user.get_id())

    form = PasswordForm(user)

    if token != '':
        del form.current

    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Password updated.")
        if not current_user.is_authenticated():
            login_user(user)
        return redirect(url_for("user.profile", username = user.username))
    return render_template("user_password.html", form=form)

@bp.route('/confirm', methods = ['GET'])
def confirm_email():
    token = request.args.get("token")
    expired, invalid, user_id = confirm_email_token_status(token)

    if invalid or expired:
        flash("Invalid token.")
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)

    user.confirmed = True
    db.session.commit()

    if user.id != current_user.get_id():
        logout_user()
        login_user(user)

    flash("Email confirmed.")
    return redirect(url_for("user.profile", username = user.username))

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@bp.route('/<username>', methods = ['GET'])
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    presentations = Presentation.query.filter_by(user_id=user.id, finished=True, published=True).order_by(db.desc(Presentation.id)).all()

    edit = user.id == current_user.get_id()

    pending = []
    if edit:
        pending = Presentation.query.filter_by(user_id=user.id).filter((Presentation.finished==False) | (Presentation.published==False)).order_by(db.desc(Presentation.id)).all()

    return render_template("user.html", user=user, presentations=presentations, pending=pending, edit=edit)

@bp.route('/<username>/image.jpg', methods = ['GET'])
def image(username):
    user = User.query.filter_by(username=username).first_or_404()

    if not user.has_image:
        return abort(404)

    return image_response(user.get_image_path())