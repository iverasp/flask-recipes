from flask import Flask, jsonify, render_template, redirect, url_for, \
    flash, session, request
from flask.ext.login import LoginManager, login_user , logout_user , \
    current_user , login_required
from flask.ext.wtf import CsrfProtect
from models import *
from forms import *
from pprint import pprint


app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
CsrfProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.before_first_request
def initialize_database():
    print "creating db"
    db.create_all()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    user = current_user

@app.route('/')
def index():
    logout_form = LogoutForm()
    return render_template(
        'index.html',
        user=current_user,
        recipes=Recipe.query.order_by(Recipe.date.desc()).all(),
        logout_form=logout_form
    )

@app.route('/recipe/<id>')
def recipe(id):
    #recipe = Recipe.query.join(User.recipes).filter(Recipe.id==id).first()
    #recipe = db.session.query(User.id).join(User.recipes)
    recipe = Recipe.query.filter_by(id=id).first()
    pprint (vars(recipe))
    print recipe.author
    logout_form = LogoutForm()
    if not recipe:
        flash('Recipe not found')
        return redirect(url_for('index'))

    return render_template(
        'show_recipe.html',
        recipe=recipe,
        logout_form=logout_form
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        registered_user = User.query.filter_by(
            username=login_form.username.data,
        ).first()
        if registered_user is None \
            or not registered_user.check_password(login_form.password.data):
            flash('Wrong phone number or password')
            return redirect(url_for('login'))
        login_user(registered_user, remember=login_form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html',
                            title='Log in',
                            login_form=login_form)

@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    recipe_form = RecipeForm()
    logout_form = LogoutForm()
    if recipe_form.validate_on_submit():
        recipe = Recipe(
            name=recipe_form.name.data,
            author=current_user,
            ingredients=recipe_form.ingredients.data,
            instructions=recipe_form.instructions.data,
            sources=recipe_form.sources.data
        )
        db.session.add(recipe)
        db.session.commit()
        flash('Recipe added')
        return redirect(url_for('recipe', id=recipe.id))
    return render_template(
        'recipe.html',
        recipe_form=recipe_form,
        logout_form=logout_form,
        categories=Category.query.all()
    )

@app.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    recipe = Recipe.query.filter_by(id=id).first()
    if not recipe or recipe.author_id is not current_user.id:
        flash('Recipe not found')
        return redirect(url_for('index'))
    logout_form = LogoutForm()
    recipe_form = RecipeForm(obj=recipe)

    categories_query = Category.query.all()
    categories = [i.name for i in categories_query]
    print "cat", categories

    if recipe_form.validate_on_submit():
        recipe.name = recipe_form.name.data
        recipe.date_edited = datetime.now()
        recipe.ingredients = recipe_form.ingredients.data
        recipe.instructions = recipe_form.instructions.data
        recipe.sources = recipe_form.sources.data
        form_categories = str(recipe_form.categories.data).split(',')
        for cat in form_categories:
            if cat not in categories:
                print "updating cateogires"
                new_category = Category(
                    name=form_categories[-1],
                    recipes=[recipe]
                    )
                db.session.add(new_category)
                db.session.commit()
        else: print "categories match"
        db.session.commit()
        flash('Recipe saved')
        return redirect(url_for('recipe', id=recipe.id))
    return render_template(
        'recipe.html',
        recipe_form=recipe_form,
        logout_form=logout_form,
        categories=categories,
        edit=True
    )

@app.route('/adduser')
def adduser():
    if User.query.filter_by(
        username='iverasp'
    ).first():
        flash('user already exists')
        return redirect(url_for('index'))
    user = User(
        username='iverasp',
        password='lolcats'
    )

    db.session.add(user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_form = LogoutForm()
    if logout_form.validate_on_submit():
        #session.clear()
        logout_user()
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    logout_form = LogoutForm()
    return render_template('404.html', logout_form=logout_form), 404

if __name__=='__main__':
    app.run(debug=True)
