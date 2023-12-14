import config
from exts import db
import datetime


class User(db.Model):
    __tablename__ = 'user'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(16), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    head = db.Column(db.String(200), nullable=True, default=config.IMAGE+'default.png')
    # email = db.Column(db.String(20), nullable=True, unique=True)
    # classroom = db.Column(db.Integer, default=0)
    target = db.Column(db.Integer, default=0)
    isRecorded = db.Column(db.Boolean, default=False)
    ContinuousDay = db.Column(db.Integer, default=0)
    TotalDay = db.Column(db.Integer, default=0)
    LastDay = db.Column(db.Date)
    TotalNumber = db.Column(db.Integer, default=0)

    def to_json(self):
        item = self.__dict__
        if "_sa_instance_state" in item:
            del item["_sa_instance_state"]
        return item


class Punch(db.Model):
    __tablename__ = 'punch'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.uid"), nullable=False)
    punch_time = db.Column(db.DateTime, default=datetime.datetime.now)
    number = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    user = db.relationship("User", backref="Punches")


class EmailCaptchaModel(db.Model):
    __tablename__ = 'email_captcha'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(20), nullable=False)
    captcha = db.Column(db.String(8), nullable=False)
    used = db.Column(db.Boolean, default=False)
