#!/usr/bin/env python3
"""
简化模型转换脚本 - PyTorch -> ONNX
（Orange Pi 上推荐直接用 ONNX Runtime）
"""

import torch
from torchvision import models
import argparse
import os

def convert_pytorch_to_onnx(model_path, onnx_path, num_classes=7):
    print("加载 PyTorch 模型...")
    model = models.efficientnet_b0(weights=None)
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, num_classes)
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()

    dummy_input = torch.randn(1, 3, 224, 224)
    os.makedirs(os.path.dirname(onnx_path), exist_ok=True)

    torch.onnx.export(
        model, dummy_input, onnx_path,
        export_params=True,
        opset_version=14,          # 更高版本更稳定
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"]
    )
    print(f"✅ ONNX 模型已保存: {onnx_path}")
    print(f"模型大小: {os.path.getsize(onnx_path)/1024:.1f} KB")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default=r"D:\disaster_monitor\models\best_disaster_classifier.pth")
    parser.add_argument("--onnx_path", default=r"D:\disaster_monitor\models\disaster_classifier.onnx")
    args = parser.parse_args()

    convert_pytorch_to_onnx(args.model_path, args.onnx_path)
    print("\n转换完成！接下来在 Orange Pi 上用 onnxruntime 加载这个 .onnx 文件即可。")