# alert/notifier.py
from sensors.led_buzzer import LedBuzzerController
from config import DEVICE_LOCATION

class Notifier:
    def __init__(self):
        self.controller = LedBuzzerController()

    def trigger_alert(self, disaster_type: str, severity: int, details: str = ""):
        print(f"\n🚨🚨🚨 灾害警报 🚨🚨🚨")
        print(f"类型: {disaster_type}")
        print(f"严重程度: {severity} 级")
        print(f"详情: {details}")
        print(f"地点: {DEVICE_LOCATION}")
        print("正在触发LED + 蜂鸣器...\n")

        self.controller.alert(disaster_type, severity)

    def cleanup(self):
        self.controller.clear_rgb()
