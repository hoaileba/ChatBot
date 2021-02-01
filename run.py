# from MyProj import 
from flask_socketio import SocketIO 
import MyProj
from dotenv import load_dotenv
import os
from MyProj.api import app, socketio
print("YESY")
load_dotenv('.env')

if __name__ == '__main__':
    socketio.run(app,port = os.getenv('FLASK_RUN_PORT'), host = os.getenv('FLASK_RUN_HOST'))
    # app.run(debug = True)
