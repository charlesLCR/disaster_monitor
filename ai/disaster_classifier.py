# ai/disaster_classifier.py
from config import ENABLE_AI, SIMULATE_SENSORS
import random

class DisasterClassifier:
    def __init__(self):
        self.disaster_types = [
            'fire', 'flood', 'landslide', 'tree_fall',
            'house_damage', 'road_collapse', 'road_block'
        ]

    def analyze(self, frame, sensor_data: dict):
        """
        核心分析函数
        返回: {'disaster_type': str or None, 'confidence': float, 'details': str}
        """
        if not ENABLE_AI:
            return {"disaster_type": None, "confidence": 0.0, "details": "AI未启用"}

        # ==================== 占位逻辑（后续替换为真实模型） ====================
        # 当前使用简单规则融合，方便调试
        smoke = sensor_data.get('smoke', {}).get('value', 0)
        temp = sensor_data.get('dht', {}).get('temp', 0)
        rain = sensor_data.get('rain', {}).get('triggered', 0)
        vib = sensor_data.get('vibration', {}).get('triggered', 0)
        audio = sensor_data.get('audio', {}).get('triggered', 0)

        disaster_type = None
        confidence = 0.0
        details = ""

        # 简单规则示例（可大幅扩展）
        if smoke > 650 and temp > 42:
            disaster_type = 'fire'
            confidence = 0.75
            details = "烟雾+高温，可能发生火情"
        elif rain and vib and audio:
            disaster_type = 'landslide'
            confidence = 0.65
            details = "雨量+振动+声音异常，疑似山体滑坡"
        elif rain and vib:
            disaster_type = 'flood'
            confidence = 0.55
            details = "持续降雨+振动，注意洪涝风险"
        # TODO: 加入图像分析（OpenCV颜色/边缘/运动检测）
        # TODO: 加载onnxruntime或tflite模型进行视觉分类

        if disaster_type is None and SIMULATE_SENSORS and random.random() < 0.15:
            # 模拟偶尔触发（调试用）
            disaster_type = random.choice(self.disaster_types)
            confidence = round(random.uniform(0.6, 0.9), 2)
            details = f"模拟触发: {disaster_type}"

        return {
            "disaster_type": disaster_type,
            "confidence": confidence,
            "details": details
        }
