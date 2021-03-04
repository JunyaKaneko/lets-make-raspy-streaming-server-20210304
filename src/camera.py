import os
import time
from enum import Enum
from picamera import PiCamera


class CameraIsNotStarted(Exception):
    pass


class CameraState(Enum):
    SLEEP = 0
    ACTIVE = 1


class Camera:
    def __init__(self, work_dir='/tmp', resolution=(320, 240)):
        self._camera = PiCamera()
        self._camera.resolution = resolution
        self._camera.rotation = 180
        self._is_started = False
        self._work_dir = work_dir
        self._lock_path = os.path.join(self._work_dir, 'camera_lock')
        self._sleep_flg = os.path.join(os.path.join(self._work_dir, 'camera_sleep'))

    def __del__(self):
        self.stop()

    def _lock(self):
        open(self._lock_path, 'w').close()

    def _unlock(self):
        if os.path.exists(self._lock_path):
            os.remove(self._lock_path)

    def rotate(self, theta):
        self._camera.rotation = theta

    def start(self):
        if not self._is_started:
            self._camera.start_preview()
            self._is_started = True
            time.sleep(3)

    def stop(self):
        self._camera.stop_preview()
        self._unlock()
        self._is_started = False
        if os.path.exists(self._sleep_flg):
            os.remove(self._sleep_flg)

    @property
    def state(self):
        if os.path.exists(self._sleep_flg):
            return CameraState.SLEEP
        else:
            return CameraState.ACTIVE

    def capture(self):
        if not self._is_started:
            raise CameraIsNotStarted()
        self._lock()
        self._camera.capture(os.path.join(self._work_dir, 'camera_out.jpg'))
        self._unlock()

    def stream(self, fps=20):
        while True:
            if self.state == CameraState.ACTIVE:
                self.capture()
            time.sleep(1 / fps)


if __name__ == '__main__':
    camera = Camera()
    camera.start()
    camera.stream(20)

