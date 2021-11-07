from app import db
from flask_login import UserMixin
from datetime import datetime as dt, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app import login
import secrets

followers = db.Table(
    'followers',
    db.Column('follower_id',db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id',db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))
    icon = db.Column(db.Integer)
    token = db.Column(db.String, index=True, unique=True)
    token_exp = db.Column(db.DateTime)
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    poke_roster = db.relationship('Pokemon', backref='trainer', lazy='dynamic')
    followed = db.relationship('User',
                    secondary = followers,
                    primaryjoin=(followers.c.follower_id == id),
                    secondaryjoin=(followers.c.followed_id == id),
                    backref=db.backref('followers',lazy='dynamic'),
                    lazy='dynamic'
                    )

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            db.session.commit()

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            db.session.commit()

    def followed_posts(self):
        followed = Post.query.join(followers, (Post.user_id == followers.c.followed_id)).filter(followers.c.follower_id == self.id)
        self_posts = Post.query.filter_by(user_id=self.id)
        all_posts = followed.union(self_posts).order_by(Post.date_created.desc())
        return all_posts

    def __repr__(self):
        return f'<User: {self.id} | {self.email}>'

    def from_dict(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data["email"]
        self.icon = data['icon']
        self.password = self.hash_password(data['password'])
        self.save()

    def get_icon_url(self):
        return f"https://avatars.dicebear.com/api/croodles/{self.icon}.svg"

    def hash_password(self, original_password):
        return generate_password_hash(original_password)

    
    def check_hashed_password(self, login_password):
        return check_password_hash(self.password, login_password)

    
    def save(self):
        db.session.add(self) 
        db.session.commit() 

    def get_token(self, exp=86400):
        current_time = dt.utcnow()
        #give back token if it's not expired
        if self.token and self.token_exp > current_time + timedelta(seconds=60):
            return self.token
        #if no token, create a token and exp date
        self.token = secrets.token_urlsafe(32)
        self.token_exp = current_time + timedelta(seconds=exp)
        self.save()
        return self.token

    def revoke_token(self):
        self.token_exp = dt.utcnow() - timedelta(seconds=61)

    @staticmethod
    def check_token(token):
        u = User.query.filter_by(token=token).first()
        if not u or u.token_exp < dt.utcnow():
            return None
        return u


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=dt.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=dt.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<id: {self.id} | Body: {self.body[:15]}>'

    def save(self):
        db.session.add(self)
        db.session.commit()

    def edit(self, body):
        self.body = body
        self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poke_name = db.Column(db.String(150))
    hit_points = db.Column(db.Integer)
    defense = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    poke_img = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<id: {self.id} | Body: {self.poke_name}>'

    def to_dict(self):
        data={
            'id':self.id,
            'poke_name':self.poke_name,
            'hit_points':self.hit_points,
            'defense':self.defense,
            'attack':self.attack,
            'poke_img':self.poke_img
        }
        return data
    
    def catch(self):
        db.session.add(self)
        db.session.commit()

    def release(self):
        db.session.delete(self)
        db.session.commit()

    def get_image_url(self):
        return self.poke_img

    



@login.user_loader
def load_user(id):
    return User.query.get(int(id))