from flask import Flask, jsonify, render_template, redirect, url_for, \
    flash, session, request, jsonify
from flask.ext.login import LoginManager, login_user , logout_user , \
    current_user , login_required
from app import app, db, login_manager
from forms import *
from models import *
import json

@app.before_first_request
def initialize_database():
    if app.debug:
        print "creating db"
        db.create_all()
    #app.jinja_env.globals.update(logout_form=LogoutForm())

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    user = current_user
    #logout_form = LogoutForm()

@app.route('/')
def index():
    return render_template(
        'index.html',
        recipes=Recipe.query.order_by(Recipe.date.desc()).all(),
        tags=Tag.query.all()
    )

@app.route('/search', methods=['POST'])
def search():
    search_form = SearchForm()
    if search_form.validate_on_submit():
        # best way of doing this?
        # todo: figure out how join works with whoosh

        result_cat = [i.serialize for i in
            db.session.query(Recipe).join(Tag.recipes)
            .filter(Tag.name.like('%'+search_form.query.data+'%')).all()]

        result_free = [i.serialize for i in
            Recipe.query.whoosh_search(search_form.query.data).all()
            if i.serialize not in result_cat]

        return jsonify(result = result_cat + result_free)

    flash('Something went wrong', 'warning')
    return redirect(url_for('index'))

@app.route('/recipe/<id>', methods=['GET', 'POST'])
def recipe(id):
    recipe = Recipe.query.filter_by(id=id).first()
    if not recipe:
        flash('Recipe not found', 'warning')
        return redirect(url_for('index'))
    recipe_tags = [i.name for i in recipe.tags.all()]
    if current_user.is_authenticated():
        comment_form = CommentForm()
        if comment_form.validate_on_submit():
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
            recipe_tags=recipe_tags,
            comment_form=comment_form,
        )
    return render_template(
        'show_recipe.html',
        title=recipe.name + ' by ' + recipe.author.username,
        recipe=recipe,
        recipe_tags=recipe_tags
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
            flash('Wrong phone number or password', 'warning')
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

    all_tags_query = Tag.query.all()
    all_tags = [i.name for i in all_tags_query]
    recipe_tags = [i.name for i in recipe.tags.all()]
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
        all_tags=all_tags,
        recipe_tags=','.join(map(str, recipe_tags)),
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
            flash('Recipe not found', 'warning')
            return redirect(url_for('index'))

    all_tags_query = Tag.query.all()
    all_tags = [i.name for i in all_tags_query]
    all_recipes = [i.name for i in Recipe.query.all()]
    print all_recipes
    if id == 'new':
        recipe_tags = []
        recipe_recipes = []
    else:
        recipe_tags = [i.name for i in recipe.tags.all()]
        recipe_recipes = [i.name for i in recipe.recipe_children.all()]
        print recipe_tags
    print "all_tags", all_tags
    print "recipe_tags", recipe_tags

    if recipe_form.validate_on_submit() and not id == 'new':
        recipe.name = recipe_form.name.data
        recipe.date_edited = datetime.now()
        recipe.ingredients = recipe_form.ingredients.data
        recipe.instructions = recipe_form.instructions.data
        recipe.sources = recipe_form.sources.data
        form_tags = [x.strip() for x in recipe_form.tags.data.split(',')]
        form_recipes = [x.strip() for x in recipe_form.recipes.data.split(',')]
        update_tags(recipe, all_tags, recipe_tags, form_tags)
        update_recipe_recipes(recipe, all_recipes, recipe_recipes, form_recipes)
        db.session.commit()
        flash('Recipe saved', 'success')
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
        form_tags = [x.strip() for x in recipe_form.tags.data.split(',')]
        form_recipes = [x.strip() for x in recipe_form.recipes.data.split(',')]
        update_tags(recipe, all_tags, recipe_tags, form_tags)
        update_recipe_recipes(recipe, all_recipes, recipe_recipes, form_recipes)
        db.session.commit()
        flash('Recipe added', 'success')
        return redirect(url_for('recipe', id=recipe.id))
    return render_template(
        'recipe.html',
        recipe_form=recipe_form,
        all_tags=all_tags,
        recipe_tags=','.join(map(unicode, recipe_tags)),
        all_recipes=all_recipes,
        recipe_recipes=','.join(map(unicode, recipe_recipes)),
        edit=edit
    )

@app.route('/delete_recipe', methods=['POST'])
@login_required
def delete_recipe():
    print 'called delete_recipe'
    delete_recipe_form = DeleteRecipeForm()
    if delete_recipe_form.validate_on_submit():
        recipe = Recipe.query.filter_by(id=delete_recipe_form.id.data).first()
        print recipe
        if not recipe.author == current_user:
            flash('Something went wrong', 'warning')
            return redirect(url_for('index'))
        db.session.delete(recipe)
        db.session.commit()
        flash('Deleted recipe')
        return redirect(url_for('index'))
    flash('Deleted recipe')
    return redirect(url_for('index'))

@app.route('/delete_comment', methods=['POST'])
@login_required
def delete_comment():
    print 'called delete_comment'
    delete_comment_form = DeleteCommentForm()
    if delete_comment_form.validate_on_submit():
        comment = Comment.query.filter_by(id=delete_comment_form.id.data).first()
        if not comment.author == current_user:
            flash('Something went wrong', 'warning')
            return redirect(url_for('index'))
        db.session.delete(comment)
        db.session.commit()
    return 'lol'

def update_tags(recipe, all_tags, old_tags, new_tags):
    print "called update_tags"
    print "old_tags", old_tags
    print "new_tags", new_tags
    pos_diff = list(set(new_tags) - set(old_tags))
    neg_diff = list(set(old_tags) - set(new_tags))
    print "pos_diff", pos_diff
    print "neg_diff", neg_diff
    for p in pos_diff:
        if p is not "": #this needs better fix!
            if p not in all_tags:
                new_cat = Tag(
                    name=p,
                    recipes=[recipe]
                    )
                db.session.add(new_cat)
            else:
                new_cat = Tag.query.filter_by(name=p).first()
                recipe.tags.append(new_cat)

    for n in neg_diff:
        del_cat = Tag.query.filter_by(name=n).first()
        recipe.tags.remove(del_cat)

def update_recipe_recipes(recipe, all_recipes, old_recipes, new_recipes):
    print "called update_recipe_recipes"
    print "old_recipes", old_recipes
    print "new_recipes", new_recipes
    pos_diff = list(set(new_recipes) - set(old_recipes))
    neg_diff = list(set(old_recipes) - set(new_recipes))
    print "pos_diff", pos_diff
    print "neg_diff", neg_diff
    for p in pos_diff:
        if p is not "": #this needs better fix!
            if p not in all_recipes:
                # alert user of error
                pass
            else:
                new_recipe = Recipe.query.filter_by(name=p).first()
                recipe.recipe_children.append(new_recipe)

    for n in neg_diff:
        del_recipe = Recipe.query.filter_by(name=n).first()
        recipe.recipe_children.remove(del_recipe)

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
        logout_user()
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
