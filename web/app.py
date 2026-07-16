# web/app.py
"""Flask Web 控制台：页面、MJPEG 视频流、云台控制 API。"""

from __future__ import annotations

import os
import sys
import threading

from flask import Flask, Response, jsonify, request, send_from_directory

# 保证以模块 / 脚本启动时都能找到项目根
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from camera_service import get_camera_service
from config import POSITIONS, WEB_HOST, WEB_PORT
from web.runtime import attach_hardware, get_motor, get_sensor_snapshot, motor_lock

WEB_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=WEB_DIR, static_url_path="")


@app.route("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/video_feed")
def video_feed():
    camera = get_camera_service()
    return Response(
        camera.mjpeg_generator(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/api/motor/rotate", methods=["POST"])
def motor_rotate():
    motor = get_motor()
    if motor is None:
        return jsonify({"ok": False, "error": "电机未初始化"}), 503

    data = request.get_json(silent=True) or {}
    if "angle" not in data:
        return jsonify({"ok": False, "error": "缺少 angle 参数"}), 400

    try:
        angle = int(data["angle"])
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "angle 必须是整数"}), 400

    if angle not in POSITIONS:
        return jsonify({
            "ok": False,
            "error": f"角度必须是 {POSITIONS} 之一",
            "allowed": POSITIONS,
        }), 400

    with motor_lock:
        motor.rotate_to(angle)
        current = motor.current_angle

    return jsonify({"ok": True, "angle": current})


@app.route("/api/status")
def status():
    camera = get_camera_service()
    motor = get_motor()
    return jsonify({
        "ok": True,
        "camera_opened": camera.is_opened(),
        "current_angle": getattr(motor, "current_angle", None) if motor else None,
        "allowed_angles": POSITIONS,
        "sensors": get_sensor_snapshot(),
    })


def start_web_server(background: bool = True) -> threading.Thread | None:
    """在后台线程启动 Flask（供 main.py 调用）。"""
    def _run():
        # 关闭 reloader，避免双进程重复打开摄像头
        app.run(host=WEB_HOST, port=WEB_PORT, debug=False, threaded=True, use_reloader=False)

    if background:
        t = threading.Thread(target=_run, name="flask-web", daemon=True)
        t.start()
        print(f"[Web] 控制台已启动: http://{WEB_HOST}:{WEB_PORT}/")
        return t

    _run()
    return None


def create_standalone():
    """仅启动 Web + 摄像头 + 电机（不跑巡检主循环）。"""
    from sensors.camera_motor import CameraMotor
    from sensors.dht import DHTSensor
    from sensors.rain import RainSensor
    from sensors.vibration import VibrationSensor
    from sensors.smoke import SmokeSensor
    from sensors.audio import AudioSensor

    camera = get_camera_service()
    camera.start()

    motor = CameraMotor()
    dht, rain, vib, smoke, audio = (
        DHTSensor(), RainSensor(), VibrationSensor(), SmokeSensor(), AudioSensor()
    )

    def snapshot():
        return {
            "dht": dht.read(),
            "rain": rain.read(),
            "vibration": vib.read(),
            "smoke": smoke.read(),
            "audio": audio.read(),
        }

    attach_hardware(motor, snapshot)
    print(f"[Web] 独立模式: http://{WEB_HOST}:{WEB_PORT}/")
    start_web_server(background=False)


if __name__ == "__main__":
    create_standalone()
