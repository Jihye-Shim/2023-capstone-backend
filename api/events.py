#socket event
from flask_socketio import emit, join_room, leave_room, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from .db import User, Log
from .model import predict
import datetime

class ChatNamepsace(Namespace):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input = {}
        self.input_time = {}

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
        self.input_time[uid] = time
        self.input[uid] = log

    #bot reply emit(output data by chatbot model)
    @jwt_required()
    def on_sendreply(self, data):
        uid = get_jwt_identity()
        user = User.query.filter_by(id=uid).first()
        answer = predict(str(data["input"]), user.major)
        log = str(answer).replace(' / ', '\n')
        emit('reply', {"msg": log}, room=user.id)
        time = datetime.datetime.now()
        Log.save_log(uid, self.input[uid], log, self.input_time[uid], time, None, None)
        del self.input[uid]
        del self.input_time[uid]