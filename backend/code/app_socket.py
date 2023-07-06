from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO

import config


app = Flask(__name__)
app.config.from_object(config)
CORS(app)
socketio = SocketIO(app, async_mode='eventlet')


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('send')
def chat(data):
    socketio.emit('get', data)


@socketio.on('test')
def test():
    socketio.send("test")

if __name__ == "__main__":
    # app.run('10.7.6.223', port=9485)
    socketio.run(app, '10.7.6.223', port=9485, keyfile='./static/g-yt-k8s.key', certfile='./static/g-yt-k8s.crt')
