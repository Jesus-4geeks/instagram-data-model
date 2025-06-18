from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Relaciones
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    
    # Relaciones de seguimiento
    following = db.relationship(
        'Follower',
        foreign_keys='Follower.user_from_id',
        backref='follower_user',
        lazy='dynamic'
    )
    
    followers = db.relationship(
        'Follower',
        foreign_keys='Follower.user_to_id',
        backref='followed_user',
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email
        }

class Post(db.Model):
    __tablename__ = 'post'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relaciones
    media = db.relationship('Media', backref='post', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Post {self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "media": [media.serialize() for media in self.media],
            "comments": [comment.serialize() for comment in self.comments]
        }

class Media(db.Model):
    __tablename__ = 'media'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(MediaType), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f'<Media {self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "url": self.url,
            "post_id": self.post_id
        }

class Comment(db.Model):
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    comment_text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f'<Comment {self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "comment_text": self.comment_text,
            "author_id": self.author_id,
            "post_id": self.post_id
        }

class Follower(db.Model):
    __tablename__ = 'follower'
    
    id = db.Column(db.Integer, primary_key=True)
    user_from_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Constraint para evitar auto-seguimiento y duplicados
    __table_args__ = (
        db.UniqueConstraint('user_from_id', 'user_to_id', name='unique_follow'),
        db.CheckConstraint('user_from_id != user_to_id', name='no_self_follow')
    )

    def __repr__(self):
        return f'<Follower {self.user_from_id} -> {self.user_to_id}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_from_id": self.user_from_id,
            "user_to_id": self.user_to_id
        }