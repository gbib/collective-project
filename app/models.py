from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('BloodRequest', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = BloodRequest.query.join(
            followers, (followers.c.followed_id == BloodRequest.user_id)).filter(
            followers.c.follower_id == self.id)
        own = BloodRequest.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(BloodRequest.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    language = db.Column(db.String(5))
    blood_group_id = db.Column(db.Integer, db.ForeignKey('blood_group.id', use_alter=True), nullable=True)
    location = db.Column(db.String(256))
    person_name = db.Column(db.String(256))
    description = db.Column(db.String(1024))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', use_alter=True), nullable=True)
    donations = db.relationship('Donation', backref='destination', lazy='dynamic')

    def __repr__(self):
        return '<BloodRequest {}>'.format(self.body)


class Donation(db.Model):
    """
    Class for representing the Donation model
    @donation_id - primary key: int
    @donor_id - foreign key: int
    @date - donation date: DateTime
    @request_id - foreign key: int
    @accepted - flag which is false by default, true if the the donation was accepted
    """

    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id', use_alter=True), nullable=False)
    date = db.Column(db.DateTime)
    request_id = db.Column(db.Integer, db.ForeignKey('blood_request.id', use_alter=True), nullable=True)
    accepted = db.Column(db.Boolean, default=False)

    def get_id(self):
        return self.id

    def __repr__(self):
        return "<Donation: id: {0}, donor_id: {1}, date: {2}>".format(
            self.id, self.donor_id, self.date
        )

    def to_map(self):
        return {
            "id": self.id,
            "donor_id": self.donor_id,
            "date": self.date,
            "request_id": self.request_id,
            "accepted": self.accepted
        }


class BloodGroup(db.Model):
    """
    Class for representing BloodGroup model
    @id - primary key: int
    @name - group type: string
    @rh - group's rh (+, -): string
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(2), unique=False)
    rh = db.Column(db.String(1), unique=False)

    def __repr__(self):
        return "<Blood Group: id: {0}, name: {1}, rh: {2}>".format(
            self.id, self.name, self.rh
        )

    def get_id(self):
        return self.id

    def to_map(self):
        return {
            "blood_group_id": self.id,
            "name": self.name,
            "rh": self.rh
        }
