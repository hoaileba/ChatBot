# from MyProj import 
from flask_socketio import SocketIO 
import MyProj
from dotenv import load_dotenv
from MyProj.api import app, socketio
print("YESY")
load_dotenv('.env')

if __name__ == '__main__':
    socketio.run(app,debug=True,port = app.config['FLASK_RUN_PORT'], host = app.config['FLASK_RUN_HOST'])
    # app.run(debug = True)