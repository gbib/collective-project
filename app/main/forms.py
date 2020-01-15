from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User, BloodGroup


# def get_blood_group_choices():
#     blood_groups = BloodGroup.query.get_all()
#     return [(blood_group.id, blood_group.name + " " + str(blood_group.rh)) for blood_group in blood_groups]


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    blood_group = SelectField(_l('Blood group'), choices=[('1', "0 -"), ('2', "A2 -"), ('3', "B3 -"), ('4', "AB -"), ('5', "0 +"),
                                                      ('6', "A2 +"), ('7', "B3 +"), ('8', "AB +")],
                          validators=[DataRequired()])
    phone_number = StringField(_l('Phone Number'), validators=[DataRequired(), Length(min=10, max=20)])
    national_id = StringField(_l('National id'), validators=[DataRequired(), Length(min=0, max=20)])
    diseases = StringField(_l('Diseases'), validators=[Length(min=0, max=1024)])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=1024)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))
    # TODO validate form fields


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))
