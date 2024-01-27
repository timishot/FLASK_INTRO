from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flashblog import db, bcrypt
from flashblog.models import User, Post
from flashblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from flashblog.users.utils import save_picture, send_reset_email, send_email

users = Blueprint('users', __name__)

@users.before_request
def before_request():
	if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5] != 'users.':
		return redirect(url_for('users.unconfirmed'))

@users.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous() or current_user.confirmed:
		 return redirect(url_for('main.home'))
	return render_template('auth/unconfirmed.html')

@users.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email('auth/email/confirm',
	'Confirm Your Account', user=current_user, token=token)
	flash('A new confirmation email has been sent to you by email.')
	return redirect(url_for('main.home'))

@users.route("/register", methods=['POST', 'GET'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hash_password)
		db.session.add(user)
		db.session.commit()
		token = user.get_reset_token()
		send_email(user.email, 'Confirm Your Account',
'auth/email/confirm', user=user, token=token)
		flash('A confirmation email has been sent to you by email.')
		# flash(f'Your account has been created! you are now able to log in', 'success')
		return redirect(url_for('users.login'))
	return render_template('register.html', title='Register', form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('main.home'))
		else:
			flash('Log in unsuccessful, Please check email and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('main.home'))

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('users.account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_img/' + current_user.image_file)
	return render_template('account.html', title='Acccount', image_file=image_file, form=form)


@users.route("/user/<string:username>")
@login_required
def user_posts(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(Author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template("user_posts.html", posts=posts, user=user)

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instruction to reset your password.', 'info')
		return redirect(url_for('users.login'))
	return render_template('reset_request.html', title='reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.home')) 
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('users.reset_request'))
	
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hash_password
		db.session.commit()
		flash(f'Your password has been updated! you are now able to log in', 'success')
		return redirect(url_for('users.login'))
	return render_template('reset_token.html', title='Reset Password', form=form)

@users.route("/confirm/<token>", methods=['GET', 'POST'])
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.home'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('users.home'))