import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, 'configuration.config')

from routes import *
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.register_blueprint(bp)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

from routes.socket import *

socketio.init_app(app)

if __name__ == "__main__":
    socketio.run(app, debug=True)