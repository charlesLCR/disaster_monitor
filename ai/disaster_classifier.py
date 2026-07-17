# ai/disaster_classifier.py
"""
灾害识别分类器
支持两种模式:
1. 规则 + 模拟 (调试用)
2. ONNX / TFLite 模型推理 (训练后部署用)
"""

from config import ENABLE_AI, SIMULATE_SENSORS
import random
import numpy as np
import cv2

# ONNX 支持
try:
    import onnxruntime as ort

    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

# TFLite 支持（保留）
try:
    import tensorflow as tf

    TFLITE_AVAILABLE = True
except ImportError:
    TFLITE_AVAILABLE = False


class DisasterClassifier:
    def __init__(self, model_path=None):
        self.disaster_types = [
            'fire', 'flood', 'landslide', 'tree_fall',
            'house_damage', 'road_collapse', 'road_block'
        ]

        self.session = None  # ONNX session
        self.tflite_interpreter = None

        # 优先尝试加载 ONNX
        if model_path and model_path.endswith('.onnx') and ONNX_AVAILABLE:
            try:
                self.session = ort.InferenceSession(model_path)
                print(f"[AI] ONNX 模型加载成功: {model_path}")
            except Exception as e:
                print(f"[AI] ONNX 加载失败: {e}")

        # 回退到 TFLite
        elif model_path and TFLITE_AVAILABLE:
            try:
                self.tflite_interpreter = tf.lite.Interpreter(model_path=model_path)
                self.tflite_interpreter.allocate_tensors()
                self.input_details = self.tflite_interpreter.get_input_details()[0]
                self.output_details = self.tflite_interpreter.get_output_details()[0]
                print(f"[AI] TFLite 模型加载成功: {model_path}")
            except Exception as e:
                print(f"[AI] TFLite 加载失败: {e}")

    def _preprocess_image(self, frame):
        """图像预处理"""
        img = cv2.resize(frame, (224, 224))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img = (img - mean) / std
        return np.expand_dims(img, axis=0).astype(np.float32)

    def _predict(self, frame):
        """模型预测（优先 ONNX）"""
        if self.session is not None:
            input_data = self._preprocess_image(frame)
            input_name = self.session.get_inputs()[0].name
            output = self.session.run(None, {input_name: input_data})[0][0]
            pred_idx = np.argmax(output)
            confidence = float(output[pred_idx])
            disaster_type = self.disaster_types[pred_idx] if pred_idx < len(self.disaster_types) else None
            return disaster_type, confidence

        # TFLite 回退
        if self.tflite_interpreter is not None:
            input_data = self._preprocess_image(frame)
            self.tflite_interpreter.set_tensor(self.input_details['index'], input_data)
            self.tflite_interpreter.invoke()
            output = self.tflite_interpreter.get_tensor(self.output_details['index'])[0]
            pred_idx = np.argmax(output)
            confidence = float(output[pred_idx])
            disaster_type = self.disaster_types[pred_idx] if pred_idx < len(self.disaster_types) else None
            return disaster_type, confidence

        return None, 0.0

    def analyze(self, frame, sensor_data: dict):
        if not ENABLE_AI:
            return {"disaster_type": None, "confidence": 0.0, "details": "AI未启用"}

        # 使用模型预测
        disaster_type, confidence = self._predict(frame)

        if disaster_type and confidence > 0.5:
            details = f"模型预测: {disaster_type} (置信度 {confidence:.2f})"

            # 传感器融合
            smoke = sensor_data.get('smoke', {}).get('value', 0)
            temp = sensor_data.get('dht', {}).get('temp', 0)
            if disaster_type == 'fire' and smoke > 500 and temp > 38:
                details += " | 传感器确认火情"
                confidence = min(confidence + 0.15, 0.98)

            return {
                "disaster_type": disaster_type,
                "confidence": round(confidence, 3),
                "details": details
            }

        # 回退到规则
        return self._rule_based_analyze(sensor_data)

    def _rule_based_analyze(self, sensor_data):
        # 保留你原来的规则逻辑
        smoke = sensor_data.get('smoke', {}).get('value', 0)
        temp = sensor_data.get('dht', {}).get('temp', 0)
        rain = sensor_data.get('rain', {}).get('triggered', 0)
        vib = sensor_data.get('vibration', {}).get('triggered', 0)
        audio = sensor_data.get('audio', {}).get('triggered', 0)

        disaster_type = None
        confidence = 0.0
        details = ""

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

        if disaster_type is None and SIMULATE_SENSORS and random.random() < 0.15:
            disaster_type = random.choice(self.disaster_types)
            confidence = round(random.uniform(0.6, 0.9), 2)
            details = f"模拟触发: {disaster_type}"

        return {
            "disaster_type": disaster_type,
            "confidence": confidence,
            "details": details
        }