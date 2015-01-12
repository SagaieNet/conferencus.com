from flask_wtf import Form
from wtforms import TextField, BooleanField, PasswordField, FileField, TextAreaField, DateField, validators
from ..models import Admin, User

class LoginForm(Form):
    email       = TextField(u'Email', validators = [validators.required()])
    password    = PasswordField(u'Password', validators = [validators.required()])
    remember_me = BooleanField('Remember Me', default = False)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = Admin.query.filter_by(email=self.email.data).first()
        if user is None:
            self.email.errors.append(u'Unknown email')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append(u'Invalid password')
            return False

        self.user = user
        return True

class PresentationForm(Form):
    title = TextField('Title', validators = [validators.Required()])
    published = BooleanField('Published', default=False)
    abstract = TextAreaField('Abstract')
    video = TextField('Video Link', validators = [validators.Optional(), validators.URL()])

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

class PageForm(Form):
    title = TextField('Title', validators = [validators.Required()])
    url = TextField('Url', validators = [validators.Required()])
    content = TextAreaField('Text', validators = [validators.Required()])