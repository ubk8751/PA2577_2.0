from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(80), unique=True, nullable=False)
    email       = db.Column(db.String(120), unique=True, nullable=False)
    tasks       = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    userid      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task        = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(360), nullable=False)