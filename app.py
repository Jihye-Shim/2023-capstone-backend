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

# 로그인 서버
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        uid = request.form.get('uid')
        upw = request.form.get('upw')
        print(uid)
        #auth(id: str, password: str, methods: Authenticator)
        result = auth(id=uid, password=upw, methods=ClassicSession)
        if result.is_auth:
            return redirect(url_for("chat"))
        else:
            #return redirect(url_for("login"))
            return render_template("login.html")    

#소켓 서버 run
if __name__ == '__main__':
    socketio.run(app)