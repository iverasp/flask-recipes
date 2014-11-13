from flask.ext.wtf import Form, RecaptchaField
from wtforms import StringField, BooleanField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField

#def enabled_categories():
    #return Category.query.all()

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class RecipeForm(Form):
    name = StringField('name', validators=[DataRequired()])
    ingredients = TextAreaField('ingredients', validators=[DataRequired()])
    instructions = TextAreaField('instructions', validators=[DataRequired()])
    sources = TextAreaField('instructions')
    categories = TextAreaField('categories')

class CommentForm(Form):
    comment = TextAreaField('comment', validators=[DataRequired()])

class LogoutForm(Form):
    pass
