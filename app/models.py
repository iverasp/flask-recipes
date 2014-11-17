from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import unicodedata #still needed?
import flask.ext.whooshalchemy as whooshalchemy
from app import app
from app import db

#db = SQLAlchemy()
Base = declarative_base()

tag_assoc = db.Table('tag_assoc',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

recipe_assoc = db.Table('recipe_assoc',
    db.Column('parent_recipe_id', db.Integer, db.ForeignKey('recipe.id')),
    db.Column('child_recipe_id', db.Integer, db.ForeignKey('recipe.id'))
)

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    admin = db.Column(db.Boolean, nullable=False)

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

    # functions below are required for Flask-login
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

class Tag(db.Model):
    __tablename__ = 'tag'
    __searchable__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    recipes = db.relationship('Recipe', secondary=tag_assoc,
        backref=db.backref('tags', lazy='dynamic'))

    def get_name(self):
        return self.name.encode('ascii', 'ignore')

class Recipe(db.Model):
    __tablename__ = 'recipe'
    __searchable__ = ['name', 'ingredients', 'instructions']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    date_edited = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User',
                                backref=db.backref('recipe',lazy='dynamic'))
    ingredients = db.Column(db.String)
    instructions = db.Column(db.String)
    sources = db.Column(db.String)
    children = db.relationship('Recipe', secondary=recipe_assoc,
        primaryjoin=recipe_assoc.c.parent_recipe_id==id,
        secondaryjoin=recipe_assoc.c.child_recipe_id==id,
        backref=db.backref('recipe_children', lazy='dynamic'))

    parents = db.relationship('Recipe', secondary=recipe_assoc,
        primaryjoin=recipe_assoc.c.child_recipe_id==id,
        secondaryjoin=recipe_assoc.c.parent_recipe_id==id,
        backref=db.backref('recipe_parents', lazy='dynamic'),
        viewonly=True)

    def has_children(self):
        print self.children
        return len(self.parents)

    def has_parents(self):
        print self.parents
        return len(self.children)

    # data for jsonify
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def get_date_pretty(self):
        return unicode(str(self.date.year) + '-' + str(self.date.month) + '-' + str(self.date.day))

    def get_date_edited_pretty(self):
        return unicode(str(self.date_edited.year) + '-' + str(self.date_edited.month) + '-' + str(self.date_edited.day))

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    date_edited = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User',
                                backref=db.backref('comment',lazy='dynamic'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    recipe = db.relationship('Recipe',
                                backref=db.backref('comment', lazy='dynamic'))

    def get_date_pretty(self):
        return unicode(str(self.date.year) + '-' + str(self.date.month) + '-' + str(self.date.day))

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String, nullable=False)

whooshalchemy.whoosh_index(app, Recipe)
whooshalchemy.whoosh_index(app, Tag)
