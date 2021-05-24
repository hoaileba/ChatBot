import numpy as np
import tensorflow as tf
import pandas as pd
import os
import time
import json
from flask import Flask
from . import NLP

# import os

from flask import Flask

# from . import db
from flask import Blueprint
from . import db

main_blue = Blueprint('main', __name__)


from flask_socketio import SocketIO 
socketio = SocketIO()

def create_app(test_config=None):
    # create and configure the app
    instance_path = "MyProj/models"
    app = Flask(__name__, instance_relative_config=True)
    app.register_blueprint(main_blue)
    app.config.from_pyfile('settings.py')
    # print(app.con fig)
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(instance_path, 'database'),
    # )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    db.init_app(app)
    # rocketio.init_app(app)
    # a simple page t
    # hat says hello
    print(app.config)
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
# app = create_app()
# socketio = SocketIO(app)
from . import api
# from . import run
# app = create_app()
# if __name__ == '__main__':
#     socketio.run(app,debug=True)

#     # 
#     app.run(debug=True)

