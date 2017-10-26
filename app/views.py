from flask import render_template, flash, redirect, url_for
from app import app, db
from oauth import OAuthSignIn
from models import User
from flask_login import login_user, current_user, logout_user

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

@app.route('/login', methods=['GET', 'POST'])
def login():
  return render_template('login.html', 
    title="Sign In"
  )

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





