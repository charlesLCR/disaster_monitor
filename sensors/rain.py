from sensors.base_sensor import BaseSensor
from config import RAIN_PIN, RAIN_THRESHOLD, SIMULATE_SENSORS
import wiringpi
import random

class RainSensor(BaseSensor):
    def __init__(self):
        super().__init__(RAIN_PIN)
        if not SIMULATE_SENSORS:
            wiringpi.pinMode(RAIN_PIN, 0)  # INPUT

    def read(self):
        if SIMULATE_SENSORS:
            val = random.choice([0, 1])
        else:
            val = wiringpi.digitalRead(self.pin)
        triggered = 1 if val >= RAIN_THRESHOLD else 0
        return {"value": val, "triggered": triggered}
