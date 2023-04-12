#DB setting: MariaDB, SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)
    print("connect!")
    
def create_all():
    db.create_all()
    
#user table
class User(db.Model):
    __tablename__ = 'test_user'
    id = db.Column(db.String(10), primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    major = db.Column(db.String(30), nullable=False)
    grade = db.Column(db.String(3), nullable=False)

    def __init__(self, user_id, username, major, grade):
        self.id = user_id
        self.username = username
        self.major = major
        self.grade = grade

    def __repr__(self):
        return f"{self.__class__.__tablename__}(id={self.id}, username={self.username}, major={self.major}, grade={self.grade})"

#user message table
class Input(db.Model):
    __tablename__ = 'test_input'
    input_id = db.Column(db.INTEGER, primary_key=True)
    user_id = db.Column(db.String(10), db.ForeignKey("test_user.id"), nullable=False)
    message = db.Column(db.String(400), nullable=False)
    time = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __init__(self, input_id, user_id, message):
        self.input_id = input_id
        self.user_id = user_id
        self.message = message

    def __repr__(self):
        return f"{self.__class__.__tablename__}(input_id={self.input_id}, user_id={self.user_id}, message={self.message}, time={self.time})"
    
#chatbot reply table
class Output(db.Model):
    __tablename__ = 'test_output'
    output_id = db.Column(db.INTEGER, primary_key=True)
    input_id = db.Column(db.INTEGER, db.ForeignKey("test_input.input_id"), nullable=False)
    reply = db.Column(db.String(400), nullable=False)
    time = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __init__(self, output_id, input_id, user_id, message):
        self.output_id = output_id
        self.input_id = input_id
        self.user_id = user_id
        self.message = message

    def __repr__(self):
        return f"{self.__class__.__tablename__}(output_id={self.output_id}, input_id={self.input_id}, reply={self.reply}, time={self.time})"