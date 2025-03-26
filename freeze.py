from flask import Flask
from flask_frozen import Freezer

app = Flask(__name__)
app.config['FREEZER_DESTINATION'] = 'build'

@app.route('/')
def index():
    return 'Hello, Static World!'

freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()