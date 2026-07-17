# sensors/camera_motor.py
import time
from config import MOTOR_PAN_PINS, SIMULATE_SENSORS

try:
    import wiringpi
    HAS_WIRINGPI = True
except ImportError:
    wiringpi = None
    HAS_WIRINGPI = False


class CameraMotor:
    def __init__(self):
        self.pins = MOTOR_PAN_PINS
        self.sequence = [
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 0, 0, 1],
        ]
        self.current_angle = 0
        self.simulate = SIMULATE_SENSORS or not HAS_WIRINGPI

        if self.simulate:
            reason = "SIMULATE_SENSORS=True" if SIMULATE_SENSORS else "wiringpi 不可用"
            print(f"[Motor] 模拟模式（{reason}）")
            return

        wiringpi.wiringPiSetup()
        for pin in self.pins:
            wiringpi.pinMode(pin, 1)  # OUTPUT

    def rotate_to(self, target_angle):
        """旋转到目标角度（度）"""
        target_angle = int(target_angle)
        diff = target_angle - self.current_angle
        if diff == 0:
            return

        if self.simulate:
            time.sleep(min(1.5, abs(diff) / 180.0 * 0.6 + 0.2))
            self.current_angle = target_angle
            print(f"[Motor] 模拟旋转到 {target_angle}°")
            return

        direction = 1 if diff > 0 else -1
        steps = int(abs(diff) / 360.0 * 4096)
        seq = self.sequence if direction > 0 else self.sequence[::-1]

        for i in range(steps):
            step = seq[i % 8]
            for pin, value in zip(self.pins, step):
                wiringpi.digitalWrite(pin, value)
            time.sleep(0.001)

        self.current_angle = target_angle
        for pin in self.pins:
            wiringpi.digitalWrite(pin, 0)

    def capture_at_position(self, angle, camera_service=None):
        """旋转到角度并取当前共享摄像头帧。"""
        print(f"[Motor] 正在旋转到 {angle}° ...")
        self.rotate_to(angle)
        time.sleep(1.2)
        if camera_service is None:
            from camera_service import get_camera_service
            camera_service = get_camera_service()
        return camera_service.get_frame()

    def cleanup(self):
        if self.simulate or not HAS_WIRINGPI:
            return
        for pin in self.pins:
            wiringpi.digitalWrite(pin, 0)
