from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


class PokeForm(FlaskForm):
    poke_id = StringField('Search for a Pokemon', validators = [DataRequired()])
    submit = SubmitField('Submit')