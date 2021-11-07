from .import bp as social
from flask import render_template, flash, redirect, url_for, request
from app.blueprints.auth.models import User, Post
from flask_login import login_required, current_user

@social.route('/', methods = ['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        body=request.form.get('body')
        new_post=Post(user_id=current_user.id, body=body)
        new_post.save()
        return redirect(url_for('social.index'))
    posts=current_user.followed_posts()
    return render_template('index.html.j2', posts=posts)

@social.route('/show_users')
@login_required
def show_users():
    users= User.query.all()
    return render_template('show_users.html.j2', users = users)

@social.route('/follow/<int:id>')
@login_required
def follow(id):
    user_to_follow = User.query.get(id)
    current_user.follow(user_to_follow)
    flash(f"You are now following {user_to_follow.first_name} {user_to_follow.last_name}", 'success')
    return redirect(url_for('social.show_users'))

@social.route('/unfollow/<int:id>')
@login_required
def unfollow(id):
    user_to_unfollow = User.query.get(id)
    current_user.unfollow(user_to_unfollow)
    flash(f"You are no longer friends with {user_to_unfollow.first_name} {user_to_unfollow.last_name}", 'danger')
    return redirect(url_for('social.show_users'))

@social.route('/edit_post/<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):
    post = Post.query.get(id)
    if request.method == 'POST':
        post.edit(request.form.get('body'))
        flash("Your post has been edited", 'success')
    return render_template('edit_post.html.j2', post=post)


@social.route('/post/<int:id>')
@login_required
def get_post(id):
    post = Post.query.get(id)
    return render_template('single_post.html.j2', post = post, view_all = True)

@social.route('/post/my_posts')
@login_required
def my_posts():
    posts = current_user.posts
    return render_template('my_posts.html.j2', posts=posts)
