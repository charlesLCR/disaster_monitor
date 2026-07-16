#!/usr/bin/env python3
"""
自然灾害监测系统主程序
运行在香橙派H618上
"""

import cv2
import time
import os
from datetime import datetime

from config import *
from camera_service import get_camera_service
from sensors.camera_motor import CameraMotor
from sensors.dht import DHTSensor
from sensors.rain import RainSensor
from sensors.vibration import VibrationSensor
from sensors.smoke import SmokeSensor
from sensors.audio import AudioSensor
from ai.disaster_classifier import DisasterClassifier
from alert.notifier import Notifier
from database.db_manager import DBManager
from web.runtime import attach_hardware, motor_lock, update_sensor_snapshot


def get_severity_and_measures(disaster_type: str, confidence: float, sensor_data: dict):
    """
    占位函数：灾害程度判断 + 应对措施
    TODO: 你在这里实现具体逻辑（可根据confidence、多个传感器值综合判断）
    """
    severity = 3  # 默认中等等级
    measures = "请立即检查现场并做好疏散准备。"

    if disaster_type == 'fire':
        severity = 5 if confidence > 0.8 else 4
        measures = "立即启动消防预案，疏散人员，拨打119。"
    elif disaster_type == 'landslide':
        severity = 4
        measures = "远离山体，通知地质部门，准备应急物资。"
    elif disaster_type == 'flood':
        severity = 3
        measures = "注意水位变化，转移低洼处人员和物资。"
    # TODO: 补充其他类型

    return severity, measures


def main():
    print("=" * 50)
    print("智能摄像头自然灾害监测系统 v1.0")
    print(f"地点: {DEVICE_LOCATION}")
    print("=" * 50)

    ensure_dir(IMAGE_SAVE_DIR)

    camera = get_camera_service()
    camera.start()

    motor = CameraMotor()
    dht = DHTSensor()
    rain = RainSensor()
    vib = VibrationSensor()
    smoke = SmokeSensor()
    audio = AudioSensor()
    ai = DisasterClassifier()
    notifier = Notifier()
    db = DBManager(DB_PATH)

    def sensor_snapshot():
        return {
            "dht": dht.read(),
            "rain": rain.read(),
            "vibration": vib.read(),
            "smoke": smoke.read(),
            "audio": audio.read(),
        }

    attach_hardware(motor, sensor_snapshot)

    if WEB_ENABLED:
        from web.app import start_web_server
        start_web_server(background=True)

    print("系统初始化完成，开始巡检...\n")

    try:
        while True:
            all_sensor_data = {}

            for angle in POSITIONS:
                with motor_lock:
                    frame = motor.capture_at_position(angle, camera)
                if frame is None:
                    continue

                # 采集所有传感器
                all_sensor_data = {
                    **sensor_snapshot(),
                    "timestamp": datetime.now().isoformat(),
                }
                update_sensor_snapshot(all_sensor_data)

                dht_data = all_sensor_data["dht"]
                rain_data = all_sensor_data["rain"]
                smoke_data = all_sensor_data["smoke"]
                vib_data = all_sensor_data["vibration"]

                print(f"[{datetime.now().strftime('%H:%M:%S')}] 位置 {angle}° | "
                      f"Temp={dht_data['temp']}°C | Rain={rain_data['triggered']} | "
                      f"Smoke={smoke_data['value']} | Vib={vib_data['triggered']}")

                # AI分析
                result = ai.analyze(frame, all_sensor_data)

                if result["disaster_type"]:
                    severity, measures = get_severity_and_measures(
                        result["disaster_type"],
                        result["confidence"],
                        all_sensor_data
                    )

                    # 触发报警
                    notifier.trigger_alert(
                        result["disaster_type"],
                        severity,
                        result["details"]
                    )

                    # 保存图片（可选）
                    img_path = None
                    if SAVE_TRIGGERED_IMAGES:
                        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        img_path = os.path.join(
                            IMAGE_SAVE_DIR,
                            f"{result['disaster_type']}_{timestamp_str}.jpg"
                        )
                        cv2.imwrite(img_path, frame)
                        print(f"[保存] 触发图片: {img_path}")

                    # 写入数据库
                    db.log_disaster(
                        location=DEVICE_LOCATION,
                        disaster_type=result["disaster_type"],
                        severity=severity,
                        description=result["details"],
                        measures=measures,
                        sensor_data=all_sensor_data,
                        image_path=img_path
                    )

                time.sleep(1.5)  # 每个位置间隔

            print(f"--- 完成一轮扫描，休眠 {SCAN_INTERVAL} 秒 ---\n")
            time.sleep(SCAN_INTERVAL)

    except KeyboardInterrupt:
        print("\n用户中断，正在清理...")
    finally:
        camera.stop()
        motor.cleanup()
        notifier.cleanup()
        db.close()
        print("系统已安全退出。")


if __name__ == "__main__":
    main()
