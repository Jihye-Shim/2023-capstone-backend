#socket event
from flask_socketio import emit, join_room, leave_room, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime
import uuid
from .db import db, User, Input, Output
from .model import predict

class ChatNamepsace(Namespace):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_id = None

    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    #login
    @jwt_required()
    def on_loggedin(self, data):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        join_room(user.id)
        emit('status', {"msg": "세롱이입니다! 무엇을 도와드릴까요?"}, room=user.id)
    
    #user text emit(input data)
    @jwt_required()
    def on_sendtext(self, data):
        uid = get_jwt_identity()
        user = User.query.filter_by(id=uid).first()
        log = str(data["input"])
        emit('text', {"msg": log}, room=user.id)
        time = datetime.datetime.now()
        current_time = time.strftime("%Y%m%d-%H%M%S")
        random_string = str(uuid.uuid4()).replace("-", "")[:7]
        self.input_id =  f"{current_time}-{random_string}"
        input_log = Input(input_id=self.input_id, user_id=uid, message=log, time=time)
        db.session.add(input_log)
        db.session.commit() 
    
    #bot reply emit(output data by chatbot model)
    @jwt_required()
    def on_sendreply(self, data):
        uid = get_jwt_identity()
        user = User.query.filter_by(id=uid).first()
        answer = predict(str(data["input"]), user.major)
        log = str(answer)
        emit('reply', {"msg": log}, room=user.id)
        input_id = self.input_id
        time = datetime.datetime.now()
        current_time = time.strftime("%Y%m%d-%H%M%S")
        random_string = str(uuid.uuid4()).replace("-", "")[:7]
        output_id =  f"{current_time}-{random_string}"
        output_log = Output(output_id=output_id, input_id=input_id, reply=log, time=time)
        db.session.add(output_log)
        db.session.commit()
        

    '''
    @jwt_required()
    def on_quickbutton(self, data):
        uid = get_jwt_identity()


        emit('quick', {"msg": "button message"}, room=user)
    '''