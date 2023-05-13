#DB setting: MariaDB, SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
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
class Button(db.Model):
    __tablename__ = 'test_quickbtn'
    btn_id = db.Column(db.String(10), primary_key=True) #버튼(질문)별 고유 아이디
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
    num = db.Column(db.INTEGER, primary_key=True)
    btn_id = db.Column(db.String(10), nullable=False) #버튼(질문)별 고유 아이디
    sub_id = db.Column(db.String(10)) # 하위 -> 여러 개의 버튼 존재 가능

    def __init__(self, num, btn, sub):
        self.num= num
        self.btn_id = btn
        self.sub_id = sub
    
    def __repr__(self):
        return f"{self.__class__.__tablename__}(num={self.num}, btn_id={self.btn_id}, sub_id={self.sub_id})"

class Management(db.Model):
    __tablename__ = 'test_Manage'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(10), db.ForeignKey("test_user.id"), nullable=False)
    start = db.Column(db.Date, nullable=False)
    end = db.Column(db.Date, nullable=False)
    schedule = db.Column(db.String(200), nullable=False)

    def __init__(self, uid, start, end, schedule):
        self.user_id = uid
        self.start = start
        self.end = end
        self.schedule = schedule

    def __repr__(self):
        return f"{self.__class__.__tablename__}(id={self.id}, user_id={self.user_id}, start={self.start}, end={self.end}, schedule={self.schedule})"

class SaveLog():

    def input_log(uid, log):
        import datetime
        import uuid
        time = datetime.datetime.now()
        current_time = time.strftime("%Y%m%d-%H%M%S")
        random_string = str(uuid.uuid4()).replace("-", "")[:7]
        input_id =  f"{current_time}-{random_string}"
        input_log = Input(input_id=input_id, user_id=uid, message=log, time=time)
        db.session.add(input_log)
        db.session.commit()
        return input_id

    def output_log(input_id, log):
        import datetime
        import uuid
        time = datetime.datetime.now()
        current_time = time.strftime("%Y%m%d-%H%M%S")
        random_string = str(uuid.uuid4()).replace("-", "")[:7]
        output_id =  f"{current_time}-{random_string}"
        output_log = Output(output_id=output_id, input_id=input_id, reply=log, time=time)
        db.session.add(output_log)
        db.session.commit()