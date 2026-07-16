# sensors/base_sensor.py
import wiringpi
from abc import ABC, abstractmethod

class BaseSensor(ABC):
    def __init__(self, pin=None):
        self.pin = pin
        try:
            wiringpi.wiringPiSetup()
        except:
            pass  # 可能已经初始化

    @abstractmethod
    def read(self):
        """返回传感器当前值（统一格式）"""
        pass

    def cleanup(self):
        pass
