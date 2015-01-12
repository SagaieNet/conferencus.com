from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, PasswordField, FileField, TextAreaField, DateField, validators
from ..models import User
from ..utils import pdfinfo
import tempfile

class LoginForm(Form):
    email = TextField('Email or Username', validators = [validators.Required()])
    password = PasswordField('Password', validators = [validators.Required()])
    remember_me = BooleanField('Remember Me?', default = False)

    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(LoginForm, self).__init__(csrf_enabled=csrf_enabled, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter((User.email == self.email.data) | (User.username == self.email.data)).first()
        if user is None:
            self.password.errors.append('Invalid email and/or password')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid email and/or password')
            return False

        self.user = user
        return True

class RegisterForm(Form):
    username = TextField('Username', validators = [validators.Required(), validators.Regexp(r'^[\w.@+-]+$'), validators.Length(min=1, max=25)])
    email = TextField('Email', validators = [validators.Required(), validators.Email()])
    password = PasswordField('Password', validators = [validators.Required()])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if user is not None:
            self.username.errors.append('Username in use')
            return False

        user = User.query.filter_by(email=self.email.data).first()
        if user is not None:
            self.email.errors.append('There is already a user with the same email address')
            return False

        return True

def checkfile(form,field):
    if field.data:
        filename=field.data.filename.lower()

        ALLOWED_EXTENSIONS = set(['pdf'])
        if not ('.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS):
            raise validators.ValidationError('Wrong file type, we can only accept PDF files')

        with tempfile.NamedTemporaryFile() as temp:
            field.data.save(temp.name)

            if not pdfinfo(temp.name):
                raise validators.ValidationError('Wrong file type, we can only accept PDF files')

        # reset stream to position 0 otherwise it cannot be saved again
        field.data.stream.seek(0)

class UploadForm(Form):
    title = TextField('Title', validators = [validators.Required()])
    abstract = TextAreaField('Abstract')
    event = TextField('Event or Conference name')
    presented = DateField('Presented On', validators = [validators.Optional()])
    location = TextField('Location')
    slides_file = FileField('PDF File', validators = [validators.Required(),checkfile])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.event.data or self.presented.data or self.location.data:
            if not self.event.data:
                self.event.errors.append('This field is required.')

            if not self.presented.data:
                self.presented.errors.append('This field is required.')

            if not self.location.data:
                self.location.errors.append('This field is required.')

            if not self.event.data or not self.presented.data or not self.location.data:
                return False

        return True

class PresentationForm(Form):
    title = TextField('Title', validators = [validators.Required()])
    published = BooleanField('Published', description='Before the talk is published it is only visible to you', default = False)
    abstract = TextAreaField('Abstract')
    video = TextField('Video Link', validators = [validators.Optional(), validators.URL()])
    slides_file = FileField('PDF File', validators = [validators.Optional(), checkfile])

class EventForm(Form):
    title = TextField('Event or Conference name', validators = [validators.Required()])
    presented = DateField('Presented On', validators = [validators.Required()])
    location = TextField('Location', validators = [validators.Required()])

class LinkForm(Form):
    title = TextField('Title', validators = [validators.Required()])
    link = TextField('Link', validators = [validators.Required(),validators.URL()])

class UserForm(Form):
    email = TextField('Email', validators = [validators.Required(), validators.Email()])
    username = TextField('Username', validators = [validators.Required(), validators.Regexp(r'^[\w.@+-]+$'), validators.Length(min=1, max=25)])
    first_name = TextField('First Name')
    last_name = TextField('Last Name')
    bio = TextAreaField('Bio')
    social_twitter = TextField('Twitter Link', validators = [validators.Optional(), validators.URL()])
    social_facebook = TextField('Facebook Link', validators = [validators.Optional(), validators.URL()])
    social_github = TextField('GitHub Link', validators = [validators.Optional(), validators.URL()])
    avatar = FileField('Avatar')

    def __init__(self, user, *args, **kwargs):
        super(UserForm, self).__init__(obj=user,*args, **kwargs)
        self.user = user

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if user is not None and user.id != self.user.id:
            self.username.errors.append('Username in use')
            return False

        user = User.query.filter_by(email=self.email.data).first()
        if user is not None and user.id != self.user.id:
            self.email.errors.append('There is already a user with the same email address')
            return False

        return True

class PasswordForm(Form):
    current = PasswordField('Current Password', validators = [validators.Required()])
    password = PasswordField('Password', validators = [validators.Required()])

    def __init__(self, user, *args, **kwargs):
        super(PasswordForm, self).__init__(obj=user,*args, **kwargs)
        self.user = user

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.current and not self.user.check_password(self.current.data):
            self.current.errors.append('Current password is incorrect')
            return False

        return True

class PasswordResetForm(Form):
    email = TextField('Email or Username', validators = [validators.Required()])

    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(PasswordResetForm, self).__init__(csrf_enabled=csrf_enabled, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter((User.email == self.email.data) | (User.username == self.email.data)).first()
        if user is None:
            self.password.errors.append('Invalid email and/or password')
            return False

        self.user = user
        return True