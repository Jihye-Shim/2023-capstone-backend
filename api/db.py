#DB setting: MariaDB, SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)
    
def create_all():
    db.create_all()
    
#user table
class User(db.Model):
    __tablename__ = 'test_user'
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    major = db.Column(db.String(30), nullable=False)
    grade = db.Column(db.String(3), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    read_certification = db.Column(db.JSON, nullable=False)

    def __init__(self, user_id, name, major, grade, status, read_certification):
        self.id = user_id
        self.name = name
        self.major = major
        self.grade = grade
        self.status = status
        self.read_certification = json.dumps(read_certification, ensure_ascii=False)

    def __repr__(self):
        return f"{self.__class__.__tablename__}(id={self.id}, name={self.name}, major={self.major}, grade={self.grade}), status={self.status}, read_certification={json.loads(self.read_certification)}"

#user message table
class Input(db.Model):
    __tablename__ = 'test_input'
    input_id = db.Column(db.String(30), primary_key=True)
    user_id = db.Column(db.String(10), db.ForeignKey("test_user.id"), nullable=False)
    message = db.Column(db.String(400), nullable=False)
    time = db.Column(db.TIMESTAMP, nullable=False)
    visible = db.Column(db.Boolean, nullable=False)

    def __init__(self, input_id, user_id, message, time):
        self.input_id = input_id
        self.user_id = user_id
        self.message = message
        self.time = time
        self.visible = True

    def __repr__(self):
        return f"{self.__class__.__tablename__}(input_id={self.input_id}, user_id={self.user_id}, message={self.message}, time={self.time}, visible={self.visible})"
    
#chatbot reply table
class Output(db.Model):
    __tablename__ = 'test_output'
    output_id = db.Column(db.String(30), primary_key=True)
    input_id = db.Column(db.String(30), db.ForeignKey("test_input.input_id"), nullable=False)
    reply = db.Column(db.String(400), nullable=False)
    time = db.Column(db.TIMESTAMP, nullable=False)
    visible = db.Column(db.Boolean, nullable=False)

    def __init__(self, output_id, input_id, reply, time):
        self.output_id = output_id
        self.input_id = input_id
        self.reply = reply
        self.time = time
        self.visible = True

    def __repr__(self):
        return f"{self.__class__.__tablename__}(output_id={self.output_id}, input_id={self.input_id}, reply={self.reply}, time={self.time}, visible={self.visible})"
    
#quick buttion table -> 하위버튼 o
class QuickButton(db.Model):
    __tablename__ = 'test_quickbtn'
    btn_id = db.Column(db.INTEGER, primary_key=True) #버튼(질문)별 고유 아이디
    btn_title = db.Column(db.String(50), nullable=False)
    btn_message = db.Column(db.String(50), nullable=False) #버튼 클릭 시 출력될 사용자 메시지
    btn_contents = db.Column(db.String(200), nullable=False) #버튼 클릭 시 출력될 봇 메시지

    def __init__(self, btn, title, message, contents):
        self.btn_id = btn
        self.btn_title = title
        self.btn_message = message
        self.btn_contents = contents

    def __repr__(self):
        return f"{self.__class__.__tablename__}(btn_id={self.btn_id}, btn_title={self.btn_title}, , btn_message={self.btn_message}, btn_contents={self.btn_contents})"
    
class ButtonRelation(db.Model):
    __tablename__ = 'test_btnrelation'
    btn_id = db.Column(db.INTEGER, primary_key=True) #버튼(질문)별 고유 아이디
    parent_id = db.Column(db.INTEGER) # 상위
    child_id = db.Column(db.JSON) # 하위 -> 여러 개의 버튼 존재 가능

    def __init__(self, btn, parent, child):
        self.btn_id = btn
        self.parent_id = parent
        self.child_id = child
    
    def __repr__(self):
        return f"{self.__class__.__tablename__}(btn_id={self.btn_id}, parent_id={self.parent_id}, child_id={self.child_id})"


#class SmartAssistant(db.Model):
#    __tablename__ = 'test_assistant'
