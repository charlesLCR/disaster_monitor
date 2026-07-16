# config.py
# 自然灾害监测系统配置文件
# 注意：引脚为假设值，请根据实际硬件接线和实验指导书修改！

import os

# ==================== 设备基本信息 ====================
DEVICE_LOCATION = "实验楼A区-自然灾害监测点01"  # 可修改为实际位置
SCAN_INTERVAL = 10          # 完整扫描一圈的间隔（秒）
POSITIONS = [0, 60, 120, 180, 240, 300]  # 步进电机旋转角度列表（可调整）

# ==================== wiringpi 引脚定义（假设值） ====================
# 参考实验指导书 3.8 步进电机实验
# 请使用 gpio readall 或实际测试确认引脚编号（wiringpi编号）

# 步进电机 - 水平旋转 (Pan) - 假设使用实验中的 IN1-IN4
MOTOR_PAN_PINS = [3, 4, 6, 9]      # IN1, IN2, IN3, IN4

# 步进电机 - 俯仰 (Tilt) - 如果有第二个电机，取消注释并修改
# MOTOR_TILT_PINS = [10, 13, 15, 16]

# 其他传感器引脚（假设）
RAIN_PIN = 7                       # 雨量传感器 - 数字输入（高电平表示有雨）
VIBRATION_PIN = 8                  # 振动传感器 - 数字输入
SMOKE_PIN = 12                     # 烟雾传感器 - 建议模拟输入（需ADC支持）
# DHT 使用 I2C 或特殊 setup，详见实验指导书3.7

# RGB LED（假设共阴极，通过电阻接GPIO）
RGB_R_PIN = 21
RGB_G_PIN = 22
RGB_B_PIN = 23

# ==================== 蜂鸣器 (已改为GPIO直接控制) ====================
BUZZER_PIN = 24                    # 蜂鸣器GPIO引脚（假设值，请修改为实际引脚）
# 注意：原UART控制已移除，改为直接GPIO高低电平驱动蜂鸣器

# ==================== 阈值配置（可调优） ====================
RAIN_THRESHOLD = 1                 # 数字传感器：1表示触发
VIBRATION_THRESHOLD = 1
SMOKE_THRESHOLD = 600              # 模拟值示例
TEMP_HIGH_THRESHOLD = 45.0
AUDIO_RMS_THRESHOLD = 0.3          # 麦克风声音强度阈值（0-1）

# ==================== AI 与日志 ====================
ENABLE_AI = True                   # 后期模型接入后设为True
SIMULATE_SENSORS = True            # True=使用模拟数据（方便调试），False=真实读取
SAVE_TRIGGERED_IMAGES = True       # 检测到灾害时是否保存图片
IMAGE_SAVE_DIR = "triggered_images"

# 数据库
DB_PATH = "disaster_log.db"

# Web 控制台
WEB_ENABLED = True
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
CAMERA_INDEX = 0              # OpenCV 摄像头编号
CAMERA_JPEG_QUALITY = 80      # MJPEG 流 JPEG 质量

# ==================== 辅助函数 ====================
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
