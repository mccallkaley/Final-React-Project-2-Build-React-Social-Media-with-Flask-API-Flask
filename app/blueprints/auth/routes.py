from flask import render_template, request, redirect, url_for, flash
from .forms import LoginForm, RegisterForm, EditProfileForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
from .import bp as auth
from app.blueprints.auth.auth import basic_auth
from flask import g, make_response, request
from app.blueprints.auth.auth import token_auth
from app.models import *

@auth.get('/token')
@basic_auth.login_required()
def get_token():
    user = g.current_user
    token = user.get_token()
    return make_response({"token":token},200)

@auth.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        #do Login stuff
        email = request.form.get("email").lower()
        password = request.form.get("password")
                                #Database col = form inputted email
        u = User.query.filter_by(email=email).first()

        if u and u.check_hashed_password(password):
            login_user(u)
            # Give the user Feedback thats you logged in successfully
            flash('You have logged in', 'success')
            return redirect(url_for("social.index"))
        error_string = "Invalid Email password combo"
        return render_template('login.html.j2', error = error_string, form=form)
    return render_template('login.html.j2', form=form)

@auth.route('/logout')
@login_required
def logout():
    if current_user:
        logout_user()
        flash('You have logged out', 'danger')
        return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            new_user_data = {
                "first_name":form.first_name.data.title(),
                "last_name":form.last_name.data.title(),
                "email":form.email.data.lower(),
                "password": form.password.data,
                "icon":int(form.icon.data)
            }
            #create and empty user
            new_user_object = User()
            # build user with form data
            new_user_object.from_dict(new_user_data)
            # save user to database
            new_user_object.save()
        except:
            error_string = "There was an unexpected Error creating your account. Please Try again."
            return render_template('register.html.j2',form=form, error = error_string) #when we had an error creating a user
        return redirect(url_for('auth.login')) # on a post request that successfully creates a new user
    return render_template('register.html.j2', form = form) #the render template on the Get request

@auth.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    form = EditProfileForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_user_data={
                "first_name":form.first_name.data.title(),
                "last_name":form.last_name.data.title(),
                "email":form.email.data.lower(),
                "password": form.password.data,
                "icon":int(form.icon.data) if int(form.icon.data) != 9000 else current_user.icon
        }
        user=User.query.filter_by(email=form.email.data.lower()).first()
        if user and current_user.email != user.email:
            flash('Email already in use','danger')
            return redirect(url_for('auth.edit_profile'))
        try:
            current_user.from_dict(new_user_data)
            current_user.save()
            flash('Profile Update', 'success')
        except:
            flash('There was an unexpected error', 'danger')
            return redirect(url_for('auth.edit_profile'))
    return render_template('register.html.j2', form = form)


# returns all the posts the users they are following
@auth.get('/posts')
@token_auth.login_required()
def get_all_posts():
    user = g.current_user
    posts = user.followed_posts()
    response_list = []
    for post in posts:
        post_dict={
            "id":post.id,
            "body":post.body,
            "date_created":post.date_created,
            "date_updated":post.date_updated,
            "author": post.author.first_name + " " + post.author.last_name
        }
        response_list.append(post_dict)
    return make_response({"posts":response_list},200)


# returns a single post take a post id
@auth.get('/posts/<int:id>')
@token_auth.login_required()
def get_single_post(id):
    user = g.current_user
    post = Post.query.get(id)
    # check to make sure the user has access to the post
    if not user.is_following(post.author) and not post.author.id == user.id:
        return make_response("Cannot get a post for someone the user is not following", 403)
    if not post:
        return make_response(f"Post ID: {id} does not exist", 404)
    response_dict={
        "id":post.id,
        "body":post.body,
        "date_created":post.date_created,
        "date_updated":post.date_updated,
        "author": post.author.first_name + " " + post.author.last_name
    }
    return make_response(response_dict,200)


# {
#     "user_id":123,
#     "body":"the post body"
# }

# Creates a new post!
@auth.post('/posts')
@token_auth.login_required()
def post_post():
    posted_data = request.get_json()
    u = User.query.get(posted_data['user_id'])
    if not u:
        return make_response(f"User id: {posted_data['user_id']} does not exist", 404)
    if g.current_user.id != u.id:
        return make_response("You can only post for yourself", 403)
    post = Post(**posted_data)
    post.save()
    return make_response(f"Post id: {post.id} created", 200)


# delete a post
# {"id":3}
@auth.delete('/posts')
@token_auth.login_required()
def delete_post():
    posted_data = request.get_json()
    post = Post.query.get(posted_data['id'])
    if not g.current_user.id == post.user_id:
        return make_response("You can only delte your post", 403)
    if not post:
        return make_response(f"Post id: {posted_data['id']} does not exist", 404)
    post.delete()
    return make_response(f"Post id: {posted_data['id']} has been deleted",200)

# update our post as a put request (tech. this is a patch request)
# {
#     'id': 2,
#     'body': "the new body",
#     'user_id': 3
# }
@auth.put('/posts')
@token_auth.login_required()
def put_post():
    posted_data = request.get_json()
    post = Post.query.get(posted_data['id'])
    if not post:
        return make_response(f"Post id: {posted_data['id']} does not exist", 404)
    u = User.query.get(posted_data['user_id'])
    if not u:
        return make_response(f"User id: {posted_data['user_id']} does not exist", 404)
    if g.current_user.id != u.id:
        return make_response("You can only modify your own posts", 403)
    post.user_id = posted_data['user_id']
    post.body = posted_data['body']
    post.save()
    return make_response(f"Post id: {post.id} has been changed", 200)