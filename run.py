import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, 'configuration.conf')

from app import *

app = Flask(__name__)

if __name__ == "__main__":

    app.register_blueprint(bp)
    app.run(debug=True)