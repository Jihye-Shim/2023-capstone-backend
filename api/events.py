#socket event
from flask import session
from flask_socketio import emit, join_room, Namespace

class ChatNamepsace(Namespace):    
    
    def loggedin(self, data):
        user = session.get('uid')
        join_room(user)
        emit('status', {'msg': "serong"}, room=user)

    def sendtext(self, data):
        user = session.get('uid')
        print(data['msg']) #추후 db 연동
        emit('message', {'msg': session.get('uid') + ':' + data['msg']}, room=user)

    def loggedout(self, data):
        if "uid" in session:
            session.pop("uid")