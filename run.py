import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, 'configuration.conf')

from controller import *
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.register_blueprint(bp)
socketio = SocketIO(app, engineio_logger=True, logger=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)