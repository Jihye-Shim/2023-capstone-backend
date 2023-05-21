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


class Log(db.Model):
    __tablename__ = 'test_log'
    log_id = db.Column(db.String(30), primary_key=True)
    user_id = db.Column(db.String(10), db.ForeignKey("test_user.id"), nullable=False)
    input = db.Column(db.String(100), nullable=False)
    output = db.Column(db.String(400), nullable=False)
    input_time = db.Column(db.TIMESTAMP, nullable=False)
    output_time = db.Column(db.TIMESTAMP, nullable=False)
    sub = db.Column(db.JSON)
    schedule = db.Column(db.JSON)
    visible = db.Column(db.Boolean, nullable=False)

    def __init__(self, log_id, user_id, input, output, input_time, output_time, sub, schedule):
        self.log_id = log_id
        self.user_id = user_id
        self.input = input
        self.output = output
        self.input_time = input_time
        self.output_time = output_time
        self.sub = json.dumps(sub)
        self.schedule = json.dumps(schedule)
        self.visible = True

    def __repr__(self):
        return f"{self.__class__.__tablename__}(id={self.log_id},user_id ={self.user_id},input={self.input},output={self.output},input_time={self.input_time},output_time={self.output_time},sub={self.sub},schedule={self.schedule})"

    def save_log(uid, input, output, itime, otime, sub, schedule):
        import uuid
        current_time = otime.strftime("%Y%m%d-%H%M%S")
        random_string = str(uuid.uuid4()).replace("-", "")[:7]
        lid =  f"{current_time}-{random_string}"
        log = Log(log_id=lid, user_id=uid, input=input, output=output, input_time=itime, output_time=otime, sub=sub, schedule=schedule)
        db.session.add(log)
        db.session.commit()
    
    def get_log(uid):
        result = {}
        log_list = Log.query.filter_by(user_id=uid, visible=True).order_by(Log.input_time.asc()).all()
        i = 1
        for list in log_list:
            log = None
            log = {"input": list.input,
                   "output": list.output}
            if list.sub is not None:
                log["sub"] = json.loads(list.sub)
            if list.schedule is not None:
                log["schedule"] = json.loads(list.schedule)
            result[i] = log
            i+=1
        if len(log_list) == 0:
            return None
        return result

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
    __tablename__ = 'test_manage'
    id = db.Column(db.Integer, primary_key=True)
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

class UnivSchedule(db.Model):
    __tablename__='test_univschedule'
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Date, nullable=False)
    end = db.Column(db.Date, nullable=False)
    schedule = db.Column(db.String(100), nullable=False)

    def __init__(self, start, end, schedule):
        self.start = start
        self.end = end
        self.schedule = schedule

    def __repr__(self):
        return f"{self.__class__.__tablename__}(id={self.id}, start={self.start}, end={self.end}, schedule={self.schedule})"

class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(30), nullable=False)
    tel_number = db.Column(db.String(35), nullable=False)
    homepage = db.Column(db.String(50), nullable=False)
    abeek = db.Column(db.String(50), nullable=True)

    def __init__(self, id, department, location, tel, page, abeek):
        self.id = id
        self.department = department
        self.location = location
        self.tel_number = tel
        self.homepage = page
        self.abeek = abeek

    def __repr__(self):
        return f"{self.__class__.__tablename__}(id={self.id}, department={self.department}, location={self.location}, tel_number={self.tel_number}, homepage={self.homepage}, abeek={self.abeek})"

class Facilities(db.Model):
    __tablename__ = 'facilities'
    id = db.Column(db.Integer, primary_key=True)
    facilities = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(50))

    def __init__(self, id, f, name, location, time):
        self.id = id
        self.facilities = f
        self.name = name
        self.location = location
        self.time = time

    def __repr__(self):
        return f"{self.__class__.__tablename__}(id={self.id}, facilities={self.facilities}, name={self.name}, location={self.location}, time={self.time})"

