from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import unicodedata

db = SQLAlchemy()
Base = declarative_base()

cat_assoc = db.Table('cat_assoc',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    recipes = db.relationship('Recipe', secondary=cat_assoc,
        backref=db.backref('categories', lazy='dynamic'))

    def get_name(self):
        return self.name.encode('ascii', 'ignore')

class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    date_edited = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User',
                                backref=db.backref('recipe',lazy='dynamic'))
    ingredients = db.Column(db.PickleType)
    instructions = db.Column(db.String)
    sources = db.Column(db.String)
    comments = db.Column(db.String)

    def get_date_pretty(self):
        #return unicode(self.date.replace(hour=0, minute=0, second=0, microsecond=0))
        return unicode(str(self.date.year) + '-' + str(self.date.month) + '-' + str(self.date.day))

#class Comments(db.Model):
    #pass
