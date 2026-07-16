from config import AUDIO_RMS_THRESHOLD, SIMULATE_SENSORS
import random

class AudioSensor:
    def __init__(self):
        # TODO: 使用 pyaudio 或 subprocess 调用 arecord 实时采样
        pass

    def read(self):
        if SIMULATE_SENSORS:
            rms = round(random.uniform(0.05, 0.6), 3)
        else:
            rms = 0.15  # placeholder
        triggered = 1 if rms > AUDIO_RMS_THRESHOLD else 0
        return {"rms": rms, "triggered": triggered}
