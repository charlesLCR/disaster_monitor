# sensors/led_buzzer.py
# 蜂鸣器已改为GPIO直接控制（原UART版本已移除）
import wiringpi
import time
from config import (RGB_R_PIN, RGB_G_PIN, RGB_B_PIN, BUZZER_PIN,
                    SIMULATE_SENSORS)

class LedBuzzerController:
    def __init__(self):
        wiringpi.wiringPiSetup()
        for pin in [RGB_R_PIN, RGB_G_PIN, RGB_B_PIN, BUZZER_PIN]:
            wiringpi.pinMode(pin, 1)  # OUTPUT
            wiringpi.digitalWrite(pin, 0)

    def set_rgb(self, r, g, b):
        """设置RGB颜色 (0或1)"""
        wiringpi.digitalWrite(RGB_R_PIN, int(r))
        wiringpi.digitalWrite(RGB_G_PIN, int(g))
        wiringpi.digitalWrite(RGB_B_PIN, int(b))

    def clear_rgb(self):
        self.set_rgb(0, 0, 0)

    def beep(self, times=3, on_time=0.15, off_time=0.08):
        """简单蜂鸣器鸣叫"""
        for _ in range(times):
            wiringpi.digitalWrite(BUZZER_PIN, 1)
            time.sleep(on_time)
            wiringpi.digitalWrite(BUZZER_PIN, 0)
            time.sleep(off_time)

    def long_beep(self, duration=1.5):
        """长鸣"""
        wiringpi.digitalWrite(BUZZER_PIN, 1)
        time.sleep(duration)
        wiringpi.digitalWrite(BUZZER_PIN, 0)

    def alert_buzzer(self, disaster_type: str, severity: int):
        """根据灾害类型和严重程度播放不同蜂鸣模式"""
        self.clear_rgb()  # 先关灯，避免干扰

        # 不同灾害类型使用不同鸣叫模式
        if disaster_type == 'fire':
            # 火情：快速连续短鸣 + 长鸣
            for _ in range(3):
                self.beep(times=4, on_time=0.08, off_time=0.05)
                time.sleep(0.2)
            self.long_beep(0.8)
        elif disaster_type == 'landslide':
            # 滑坡：中速鸣叫
            self.beep(times=5, on_time=0.2, off_time=0.15)
        elif disaster_type == 'flood':
            # 洪涝：慢速长鸣
            for _ in range(2):
                self.long_beep(0.6)
                time.sleep(0.3)
        else:
            # 默认：根据严重程度
            if severity >= 4:
                self.beep(times=6, on_time=0.12, off_time=0.08)
            else:
                self.beep(times=3, on_time=0.2, off_time=0.1)

    def alert(self, disaster_type: str, severity: int = 3):
        """完整报警：RGB颜色 + 蜂鸣器模式"""
        print(f"[报警] 类型={disaster_type}, 严重程度={severity}级")

        # 设置对应颜色
        color_map = {
            'fire':       (1, 0, 0),      # 红
            'flood':      (0, 0, 1),      # 蓝
            'landslide':  (1, 0.6, 0),    # 橙
            'tree_fall':  (0, 1, 0),      # 绿
            'house_damage': (1, 1, 0),    # 黄
            'road_collapse': (1, 0, 1),   # 紫
            'road_block': (0.7, 0.7, 0.7) # 灰白
        }
        r, g, b = color_map.get(disaster_type, (1, 1, 1))
        self.set_rgb(r, g, b)

        # 播放蜂鸣器
        self.alert_buzzer(disaster_type, severity)

        # 报警后保持LED亮一段时间
        time.sleep(2.0)
        self.clear_rgb()
