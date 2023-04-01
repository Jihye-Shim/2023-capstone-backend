#app 초기 설정용
#key, DB connect
from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app(debug=True):
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = 'password'

    socketio.init_app(app)

    from api.events import ChatNamepsace
    socketio.on_namespace(ChatNamepsace('/chat'))

    from api.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app