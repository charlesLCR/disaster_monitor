from sensors.base_sensor import BaseSensor
from config import VIBRATION_PIN, VIBRATION_THRESHOLD, SIMULATE_SENSORS
import wiringpi
import random

class VibrationSensor(BaseSensor):
    def __init__(self):
        super().__init__(VIBRATION_PIN)
        if not SIMULATE_SENSORS:
            wiringpi.pinMode(VIBRATION_PIN, 0)

    def read(self):
        if SIMULATE_SENSORS:
            val = random.choice([0, 1])
        else:
            val = wiringpi.digitalRead(self.pin)
        triggered = 1 if val >= VIBRATION_THRESHOLD else 0
        return {"value": val, "triggered": triggered}
