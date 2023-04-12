#app initial setting
#key, DB connect (secret key)
from flask import Flask
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv
load_dotenv()

socketio = SocketIO(logger=True, engineio_logger=True)

def create_app(debug=False):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    from api.events import ChatNamepsace
    socketio.on_namespace(ChatNamepsace('/chat'))

    from api.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app)

    return app