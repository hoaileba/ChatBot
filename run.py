from MyProj import create_app,socketio
import MyProj
from dotenv import load_dotenv

print("YESY")
load_dotenv('.env')
app = create_app()

if __name__ == '__main__':
    socketio.run(app,debug=True)

# app.run(debug = True)
# api.app.run(Debug= True)
