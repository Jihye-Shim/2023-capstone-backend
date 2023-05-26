#socket event
from flask_socketio import emit, join_room, leave_room, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from .db import User, Log
import datetime
from api import chatmodel

class ChatNamepsace(Namespace):

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
        print("start")
        # emit('status', {"msg": "세롱이입니다! 무엇을 도와드릴까요?"}, room=user.id)

    #bot reply emit(output data by chatbot model)
    @jwt_required()
    def on_sendreply(self, data):
        uid = get_jwt_identity()
        user = User.query.filter_by(id=uid).first()
        answer = chatmodel.get_prediction(uid[:2], str(data["input"]), user.major)
        log = str(answer)
        emit('reply', {"msg": log}, room=user.id)
        time = datetime.datetime.now()
        Log.save_log(uid, str(data["input"]), log, time, time, None, None, None)
        #del self.input[uid]
        #del self.input_time[uid]

        