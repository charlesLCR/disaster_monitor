# sensors/dht.py
from sensors.base_sensor import BaseSensor
from config import SIMULATE_SENSORS
import random

class DHTSensor(BaseSensor):
    def __init__(self):
        super().__init__()
        # TODO: 根据实验指导书3.7实现真实读取
        # 可能需要 wiringpi.ht21dSetup 或 I2C 直接读

    def read(self):
        if SIMULATE_SENSORS:
            temp = round(random.uniform(25, 38), 1)
            humi = round(random.uniform(40, 85), 1)
            return {"temp": temp, "humi": humi}
        else:
            # TODO: 实现真实读取逻辑
            print("[DHT] TODO: 实现真实温湿度读取")
            return {"temp": 28.5, "humi": 65.0}
