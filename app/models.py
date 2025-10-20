from __future__ import annotations  # must be first
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)

    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)  # ✅ here

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('Like', backref='post', lazy=True, cascade="all, delete-orphan")
    comments = db.relationship(
        'Comment', 
         backref='post', 
         lazy=True, 
         cascade="all, delete-orphan" 
         )



class Comment(db.Model):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    date_posted: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(db.Integer, db.ForeignKey('comment.id'), nullable=True)

    # ✅ Correct self-referencing relationship
    replies: Mapped[List[Comment]] = relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy=True,
        cascade="all, delete-orphan"
    )


class Message(db.Model):
    __tablename__ = "messages"
    
    id = db.Column(db.Integer, primary_key=True)
    
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional: read/unread status
    is_read = db.Column(db.Boolean, default=False)
    
    # Relationships (optional but useful)
    sender = db.relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = db.relationship("User", foreign_keys=[receiver_id], backref="received_messages")
    
    def __repr__(self):
        return f"<Message {self.id} from {self.sender_id} to {self.receiver_id}>"
    


class Like(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
