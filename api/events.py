#socket event
from flask import session
from flask_socketio import emit, join_room, leave_room, Namespace

class ChatNamepsace(Namespace): 

    def on_connect(self):
        pass

    def on_disconnect(self):
        pass
    
    def on_loggedin(self, data):
        user = session.get("uid")
        join_room(user)
        emit('status', {"msg": "serong"}, room=user)

    def on_sendtext(self, data):
        user = session.get("uid")
        emit('text', {"msg": session.get("uid") + ':' + data["msg"]}, room=user)

    def on_sendreply(self, data):
        user = session.get("uid")
        emit('reply', {"msg": 'bot: ' + data["msg"] + "(자동응답)"}, room=user)
'''
    def on_quickbutton(self, data):
        user = session.get("uid")
        emit('quick', {"msg": "button message"}, room=user)
'''
    def on_loggedout(self, data):
        session.pop("uid")
        user = session.get("uid")
        leave_room(user)