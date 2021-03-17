import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, 'configuration.config')

from controller import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.register_blueprint(bp)

from controller.socket import *

socketio.init_app(app)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")