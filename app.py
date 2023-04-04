#main
from api import create_app, socketio 
from flask_cors import CORS
app = create_app(debug = True)
CORS(app)

# app run
if __name__ == '__main__':
    socketio.run(app)