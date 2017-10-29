from flask import render_template, flash, redirect, url_for, g
from app import app, db
from oauth import OAuthSignIn
from models import User
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from .forms import EditForm

@app.before_request
def before_request():
  g.user = current_user
  if g.user.is_authenticated:
    g.user.last_seen = datetime.utcnow()
    db.session.add(g.user)
    db.session.commit()

@app.route('/')
@app.route('/index')
def index():
  user = current_user
  posts = [ 
    { 
      'author': {'nickname': 'John'}, 
      'body': 'Beautiful day in Portland!' 
    },
    { 
      'author': {'nickname': 'Susan'}, 
      'body': 'The Avengers movie was so cool!' 
    },
    { 
      'author': {'nickname': 'Karen'}, 
      'body': 'I love donuts.' 
    }
  ]
  return render_template('index.html',
    title="Home", 
    user=user,
    posts=posts
  )

@app.route('/login')
def login():
  user = current_user
  return render_template('login.html', title="Sign In", user=user)

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
  if not current_user.is_anonymous:
    return redirect(url_for('index'))
  oauth = OAuthSignIn.get_provider(provider)
  return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
  if not current_user.is_anonymous:
    return redirect(url_for('index'))
  oauth = OAuthSignIn.get_provider(provider)
  social_id, username, email = oauth.callback()
  if social_id is None:
    flash('Authentication failed.')
    return redirect(url_for('index'))
  user = User.query.filter_by(social_id=social_id).first()
  if not user:
    user = User(social_id=social_id, nickname=username, email=email)
    db.session.add(user)
    db.session.commit()
  login_user(user, True)
  return redirect(url_for('index'))

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('index'))

@app.route('/user/<nickname>')
@login_required
def user(nickname):
  user = User.query.filter_by(nickname=nickname).first()
  if user == None:
    flash('User %s not found.' % nickname)
    return redirect(url_for('index'))
  posts = [
    { 'author': user, 'body': 'Test post #1' },
    { 'author': user, 'body': 'Test post #2 '}
  ]
  return render_template('user.html', 
    user=user, 
    posts=posts
  )

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
  form = EditForm()
  if form.validate_on_submit():
    g.user.nickname = form.nickname.data
    g.user.about_me = form.about_me.data
    db.session.add(g.user)
    db.session.commit()
    flash('Your changes have been saved')
    return redirect(url_for('edit'))
  else: 
    form.nickname.data = g.user.nickname
    form.about_me.data = g.user.about_me
  return render_template('edit.html', form=form)



