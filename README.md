# 智能摄像头自然灾害监测系统 - Python工程 (v1.1 - GPIO蜂鸣器版)

基于香橙派H618 + 智能摄像头产品原型机实验指导书开发。

## 更新说明 (2026-07-15)
- 蜂鸣器控制已从 **UART** 改为 **GPIO直接驱动**
- 移除了 pyserial 依赖
- 新增多种蜂鸣模式（火情快速短鸣、滑坡中速、洪涝慢长鸣等）
- RGB LED + 蜂鸣器联动更直观

## 功能
- 多角度摄像头巡检（步进电机驱动）
- 多传感器数据采集（雨量、振动、烟雾、温湿度、声音）
- 简单规则 + AI占位 的灾害识别（火情、洪涝、山体滑坡、树木倒伏、房屋损毁、路面塌陷、道路阻断）
- RGB LED + GPIO蜂鸣器报警（不同灾害不同颜色和鸣叫节奏）
- SQLite数据库记录 + 查询
- 模块化设计，方便后续接入真实AI模型和Web界面

## 快速开始

```bash
cd disaster_monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python3 main.py
```

按 Ctrl+C 退出。

## 查询历史记录
```bash
python3 -c "
from database.db_manager import DBManager
db = DBManager()
db.query_by_type('fire')   # 或不传参数查询全部
"
```

## 引脚说明（假设值 - 必须修改！）
所有引脚定义在 `config.py` 中，**强烈建议**根据实际接线和 `gpio readall` 命令修改。

**重点修改项**：
- `MOTOR_PAN_PINS`
- `BUZZER_PIN`（蜂鸣器GPIO）
- `RGB_R_PIN / G / B`
- 其他传感器引脚

参考：
- 步进电机：实验指导书 第3.8章
- 温湿度：实验指导书 第3.7章
- 摄像头：实验指导书 第3.6章 + OpenCV

## 蜂鸣器模式说明（GPIO版）
- **fire（火情）**：快速连续短鸣 + 长鸣（紧急）
- **landslide（滑坡）**：中速5次鸣叫
- **flood（洪涝）**：慢速长鸣两次
- 其他类型：根据严重程度自动选择短/长鸣

## 如何接入真实AI模型（后续）
1. 在 `ai/disaster_classifier.py` 的 `analyze` 方法中加载你的 `.onnx` 或 `.tflite` 模型
2. 把 `config.ENABLE_AI = True`
3. 模型输入：图像 + sensor_data dict，输出 disaster_type 和 confidence

## 如何添加Web界面（预留）
1. 把 `config.WEB_ENABLED = True`
2. 在 `web/app.py` 中实现 Flask 路由（已有框架）
3. 主循环中可通过队列或共享变量把最新frame和警报状态传给Web

## 注意事项
- 首次运行建议 `SIMULATE_SENSORS = True` 调试逻辑
- 真实运行时把模拟关闭，并实现各sensor的真实read()方法
- 蜂鸣器现在是GPIO直接控制，简单可靠
- 图片保存目录：triggered_images/

## 后续优化方向
- 加入GPS模块记录精确位置
- 多设备协同
- 更复杂的传感器融合算法
- 模型训练与部署（使用你们手册中的onnxruntime示例）

有问题随时问我！
