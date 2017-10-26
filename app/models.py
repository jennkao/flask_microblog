from app import app, db
from flask_login import LoginManager, UserMixin

lm = LoginManager(app)

class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  social_id = db.Column(db.String(64), nullable=False, unique=True)
  nickname = db.Column(db.String(64), nullable=False)
  email = db.Column(db.String(64), nullable=True)
  posts = db.relationship('Post', backref='author', lazy='dynamic')

  def __repr__(self):
    return '<User %r>' % (self.nickname)

class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  body = db.Column(db.String(140))
  timestamp = db.Column(db.DateTime)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

  def __repr__(self):
    return '<Post %r>' % (self.body)

@lm.user_loader
def load_user(id):
  return User.query.get(int(id))