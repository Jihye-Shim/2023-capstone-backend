from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
from sejong_univ_auth import ClassicSession, auth

app = Flask(__name__)

app.config['SECRET_KEY'] = 'password'
socketio = SocketIO(app)

@socketio.on('message')
def handleMessage(msg):
    print('Message:' + msg)
    socketio.send(msg, broadcast = True)

# 채팅 서버
@app.route("/chat")
def chat():
    return render_template("chat.html")

def messageReceived(methods=['GET','POST']):
    print("Message was received!!")

#소켓 서버 run
if __name__ == '__main__':
    socketio.run(app)