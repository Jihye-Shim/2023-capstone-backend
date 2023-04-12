#app initial setting
#key, DB connect (secret key)
from flask import Flask
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv
from . import db

load_dotenv()

socketio = SocketIO(logger=True, engineio_logger=True)

def create_app(debug=False):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    #DB connect
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from api.events import ChatNamepsace
    socketio.on_namespace(ChatNamepsace('/chat'))

    from api.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app