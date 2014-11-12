from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
Base = declarative_base()

'''
A Recipe is made by one User.
A Recipe can be in several Categories
A Category can contain several recipes
'''

category_association = db.Table('category_association', Base.metadata,
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))

)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    recipes = db.relationship('Recipe')

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    recipes = db.relationship('Recipe',
                secondary=category_association,
                backref=db.backref('categories', lazy='dynamic'))

class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    author = db.Column(db.Integer, db.ForeignKey('user.id'))
    ingredients = db.Column(db.PickleType)
    instructions = db.Column(db.String)
    comments = db.Column(db.String)
