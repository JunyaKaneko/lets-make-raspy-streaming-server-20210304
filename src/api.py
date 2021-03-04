# Copyright 2021 Morning Project Samurai, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR
# A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


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
