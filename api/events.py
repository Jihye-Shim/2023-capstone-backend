#socket event
from flask_socketio import emit, join_room, leave_room, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from .db import User
from .model import predict

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
        emit('status', {"msg": "serong"}, room=user.id)
    
    #user text emit(input data)
    @jwt_required()
    def on_sendtext(self, data):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        emit('text', {"msg": user_id + ':' + str(data["input"])}, room=user.id)
    
    #bot reply emit(output data by chatbot model)
    @jwt_required()
    def on_sendreply(self, data):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        answer = predict(str(data["input"]), user.major)
        emit('reply', {"msg": 'bot: ' + str(answer)}, room=user.id)

 #   def on_loggedout(self, data):
 #       print("pop")
 #       leave_room()

    '''
    def on_quickbutton(self, data):
        user = session.get("uid")
        emit('quick', {"msg": "button message"}, room=user)
    '''