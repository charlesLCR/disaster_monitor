from sensors.base_sensor import BaseSensor
from config import SMOKE_PIN, SMOKE_THRESHOLD, SIMULATE_SENSORS
import wiringpi
import random

class SmokeSensor(BaseSensor):
    def __init__(self):
        super().__init__(SMOKE_PIN)
        # TODO: 如果是模拟输入，需要类似实验中的 analogRead + ADC setup

    def read(self):
        if SIMULATE_SENSORS:
            val = random.randint(200, 900)
        else:
            # TODO: 实现模拟读取
            val = 350  # placeholder
        triggered = 1 if val > SMOKE_THRESHOLD else 0
        return {"value": val, "triggered": triggered}
