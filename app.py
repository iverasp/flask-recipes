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
        categories=Category.query.all(),
        logout_form=logout_form
    )

@app.route('/recipe/<id>', methods=['GET', 'POST'])
def recipe(id):
    recipe = Recipe.query.filter_by(id=id).first()
    if not recipe:
        flash('Recipe not found')
        return redirect(url_for('index'))
    logout_form = LogoutForm()
    recipe_cats = [i.name for i in recipe.categories.all()]
    if current_user.is_authenticated():
        comment_form = CommentForm()
        if comment_form.validate_on_submit() and current_user.is_authenticated():
            comment = Comment(
                comment=comment_form.comment.data,
                author=current_user,
                recipe=recipe
            )
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('recipe', id=recipe.id))
        return render_template(
            'show_recipe.html',
            title=recipe.name + ' by ' + recipe.author.username,
            recipe=recipe,
            recipe_cats=recipe_cats,
            logout_form=logout_form,
            comment_form=comment_form
        )
    return render_template(
        'show_recipe.html',
        title=recipe.name + ' by ' + recipe.author.username,
        recipe=recipe,
        recipe_cats=recipe_cats,
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

    all_cats_query = Category.query.all()
    all_cats = [i.name for i in all_cats_query]
    recipe_cats = [i.name for i in recipe.categories.all()]
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
        all_cats=all_cats,
        recipe_cats=','.join(map(str, recipe_cats)),
        edit=False
    )

@app.route('/add')
@login_required
def add():
    return redirect(url_for('edit', id='new'))

@app.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if id == 'new':
        edit = False
        recipe = True
        recipe_form = RecipeForm()
    else:
        edit = True
        recipe = Recipe.query.filter_by(id=id).first()
        recipe_form = RecipeForm(obj=recipe)
    if edit:
        if not recipe or recipe.author_id is not current_user.id:
            flash('Recipe not found')
            return redirect(url_for('index'))
    logout_form = LogoutForm()

    all_cats_query = Category.query.all()
    all_cats = [i.name for i in all_cats_query]
    if id == 'new':
        recipe_cats = []
    else:
        recipe_cats = [i.name for i in recipe.categories.all()]
    print "all_cats", all_cats
    print "recipe_cats", recipe_cats

    if recipe_form.validate_on_submit() and not id == 'new':
        recipe.name = recipe_form.name.data
        recipe.date_edited = datetime.now()
        recipe.ingredients = recipe_form.ingredients.data
        recipe.instructions = recipe_form.instructions.data
        recipe.sources = recipe_form.sources.data
        form_cats = str(recipe_form.categories.data).split(',')
        update_categories(recipe, all_cats, recipe_cats, form_cats)
        flash('Recipe saved')
        return redirect(url_for('recipe', id=recipe.id))
    if recipe_form.validate_on_submit() and id == 'new':
        recipe = Recipe(
            name=recipe_form.name.data,
            author=current_user,
            ingredients=recipe_form.ingredients.data,
            instructions=recipe_form.instructions.data,
            sources=recipe_form.sources.data
        )
        db.session.add(recipe)
        form_cats = str(recipe_form.categories.data).split(',')
        update_categories(recipe, all_cats, recipe_cats, form_cats)
        flash('Recipe added')
        return redirect(url_for('recipe', id=recipe.id))
    return render_template(
        'recipe.html',
        recipe_form=recipe_form,
        logout_form=logout_form,
        all_cats=all_cats,
        recipe_cats=','.join(map(str, recipe_cats)),
        edit=edit
    )

def update_categories(recipe, all_cats, old_cats, new_cats):
    print "called update_categories"
    print "old_cats", old_cats
    print "new_cats", new_cats
    pos_diff = list(set(new_cats) - set(old_cats))
    neg_diff = list(set(old_cats) - set(new_cats))
    print "pos_diff", pos_diff
    print "neg_diff", neg_diff
    for p in pos_diff:
        if p is not "": #this needs better fix!
            if p not in all_cats:
                new_cat = Category(
                    name=p,
                    recipes=[recipe]
                    )
                db.session.add(new_cat)
            else:
                new_cat = Category.query.filter_by(name=p).first()
                recipe.categories.append(new_cat)

    for n in neg_diff:
        del_cat = Category.query.filter_by(name=n).first()
        recipe.categories.remove(del_cat)
    db.session.commit()

@app.route('/adduser')
def adduser():
    if User.query.filter_by(
        username='iverasp2'
    ).first():
        flash('user already exists')
        return redirect(url_for('index'))
    user = User(
        username='iverasp2',
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
