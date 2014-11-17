from flask import Flask, jsonify, render_template, redirect, url_for, \
    flash, session, request
from flask.ext.login import LoginManager, login_user , logout_user , \
    current_user , login_required
from flask.ext.wtf import CsrfProtect
from flaskext.markdown import Markdown
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
CsrfProtect(app)

# setup markdown with proper newlines
md = Markdown(
    app,
    extensions=['nl2br'],
    safe_mode=True,
    output_format='html5'
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app import views, models
