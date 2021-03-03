import os
import time
from flask import Flask, Response, jsonify


app = Flask(__name__)

WORKDIR = '/tmp'


def capture():
    while True:
        if os.path.exists(os.path.join(WORKDIR, 'camera_lock')) or \
                os.path.exists(os.path.join(WORKDIR, 'camera_sleep')):
            continue
        with open(os.path.join(WORKDIR, 'camera_out.jpg'), 'rb') as f:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + f.read() + b'\r\n\r\n')
        time.sleep(0.5)


@app.route('/video/stream')
def stream_video():
    return Response(capture(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video/activate')
def start_video():
    sleep_flag = os.path.join(WORKDIR, 'camera_sleep')
    if os.path.exists(sleep_flag):
        os.remove(sleep_flag)
    return jsonify({'message': 'Activated'})


@app.route('/video/deactivate')
def stop_video():
    open(os.path.join(WORKDIR, 'camera_sleep'), 'w').close()
    return jsonify({'message': 'Deactivated'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
