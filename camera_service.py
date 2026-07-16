"""
共享摄像头服务：全局只打开一次 VideoCapture，供主循环与 Web MJPEG 共用。
"""

from __future__ import annotations

import threading
import time
from typing import Generator, Optional

import cv2
import numpy as np

from config import CAMERA_INDEX, CAMERA_JPEG_QUALITY


class CameraService:
    def __init__(self, camera_index: int = CAMERA_INDEX, jpeg_quality: int = CAMERA_JPEG_QUALITY):
        self.camera_index = camera_index
        self.jpeg_quality = jpeg_quality
        self._lock = threading.Lock()
        self._frame: Optional[np.ndarray] = None
        self._jpeg: Optional[bytes] = None
        self._opened = False
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._cap: Optional[cv2.VideoCapture] = None
        self._placeholder = self._make_placeholder()

    @staticmethod
    def _make_placeholder() -> np.ndarray:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (36, 42, 40)
        cv2.putText(
            frame,
            "Camera offline",
            (160, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (200, 210, 205),
            2,
            cv2.LINE_AA,
        )
        return frame

    def start(self) -> bool:
        if self._running:
            return self._opened

        self._cap = cv2.VideoCapture(self.camera_index)
        self._opened = bool(self._cap is not None and self._cap.isOpened())
        if not self._opened:
            print(f"[Camera] 无法打开摄像头 index={self.camera_index}，将输出占位画面")
            with self._lock:
                self._frame = self._placeholder.copy()
                ok, buf = cv2.imencode(
                    ".jpg",
                    self._frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality],
                )
                self._jpeg = buf.tobytes() if ok else None
        else:
            print(f"[Camera] 已打开摄像头 index={self.camera_index}")

        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, name="camera-service", daemon=True)
        self._thread.start()
        return self._opened

    def _capture_loop(self) -> None:
        while self._running:
            frame = None
            if self._opened and self._cap is not None:
                ok, grabbed = self._cap.read()
                if ok and grabbed is not None:
                    frame = grabbed

            if frame is None:
                frame = self._placeholder.copy()
                time.sleep(0.05)
            else:
                time.sleep(0.01)

            ok, buf = cv2.imencode(
                ".jpg",
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality],
            )
            jpeg = buf.tobytes() if ok else None

            with self._lock:
                self._frame = frame
                if jpeg is not None:
                    self._jpeg = jpeg

    def get_frame(self) -> Optional[np.ndarray]:
        """返回最新 BGR 帧副本，供 AI / 巡检使用。"""
        with self._lock:
            if self._frame is None:
                return None
            return self._frame.copy()

    def get_jpeg(self) -> Optional[bytes]:
        with self._lock:
            return self._jpeg

    def is_opened(self) -> bool:
        return self._opened

    def mjpeg_generator(self) -> Generator[bytes, None, None]:
        """供 Flask multipart/x-mixed-replace 使用。"""
        boundary = b"--frame"
        while True:
            jpeg = self.get_jpeg()
            if jpeg is None:
                time.sleep(0.05)
                continue
            yield (
                boundary
                + b"\r\n"
                + b"Content-Type: image/jpeg\r\n\r\n"
                + jpeg
                + b"\r\n"
            )
            time.sleep(0.04)

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        self._opened = False
        print("[Camera] 已关闭摄像头")


_camera_service: Optional[CameraService] = None
_camera_lock = threading.Lock()


def get_camera_service() -> CameraService:
    global _camera_service
    with _camera_lock:
        if _camera_service is None:
            _camera_service = CameraService()
        return _camera_service
