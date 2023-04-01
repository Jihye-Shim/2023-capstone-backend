#main
from api import create_app, socketio 

app = create_app(debug = True)
# app run
if __name__ == '__main__':
    socketio.run(app)