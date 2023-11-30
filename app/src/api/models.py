from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=False)
    task = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(360), nullable=False)
