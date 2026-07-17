import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from tqdm import tqdm
import copy

# ==================== 配置区 ====================
DATA_DIR = "data/images"
BATCH_SIZE = 32
NUM_EPOCHS = 30
LEARNING_RATE = 0.001
NUM_CLASSES = 7                   # 根据你的类别调整: fire, flood, landslide, tree_fall, house_damage, road_block, normal
MODEL_NAME = "efficientnet_b0"    # 可选: efficientnet_b0, mobilenet_v3_small, resnet18
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SAVE_PATH = "models/best_disaster_classifier.pth"
print(f"使用设备: {DEVICE}")

# ==================== 数据增强与加载 ====================
def get_data_transforms():
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                             std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                             std=[0.229, 0.224, 0.225])
    ])
    return train_transform, val_transform

def load_datasets():
    train_transform, val_transform = get_data_transforms()
    
    train_dataset = datasets.ImageFolder(
        os.path.join(DATA_DIR, "train"), 
        transform=train_transform
    )
    val_dataset = datasets.ImageFolder(
        os.path.join(DATA_DIR, "val"), 
        transform=val_transform
    )
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)
    
    class_names = train_dataset.classes
    print(f"类别: {class_names}")
    print(f"训练样本数: {len(train_dataset)}, 验证样本数: {len(val_dataset)}")
    
    return train_loader, val_loader, class_names

# ==================== 模型定义 ====================
def create_model(num_classes):
    if MODEL_NAME == "efficientnet_b0":
        model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif MODEL_NAME == "mobilenet_v3_small":
        model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
        model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
    else:
        model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    
    return model.to(DEVICE)

# ==================== 训练与验证 ====================
def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs):
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0
    
    for epoch in range(num_epochs):
        print(f"\nEpoch {epoch+1}/{num_epochs}")
        print("-" * 30)
        
        # 训练阶段
        model.train()
        running_loss = 0.0
        running_corrects = 0
        
        for inputs, labels in tqdm(train_loader, desc="Training"):
            inputs = inputs.to(DEVICE)
            labels = labels.to(DEVICE)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
        
        epoch_loss = running_loss / len(train_loader.dataset)
        epoch_acc = running_corrects.double() / len(train_loader.dataset)
        print(f"Train Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")
        
        # 验证阶段
        model.eval()
        val_loss = 0.0
        val_corrects = 0
        
        with torch.no_grad():
            for inputs, labels in tqdm(val_loader, desc="Validating"):
                inputs = inputs.to(DEVICE)
                labels = labels.to(DEVICE)
                
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item() * inputs.size(0)
                val_corrects += torch.sum(preds == labels.data)
        
        val_loss = val_loss / len(val_loader.dataset)
        val_acc = val_corrects.double() / len(val_loader.dataset)
        print(f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f}")
        
        # 保存最佳模型
        if val_acc > best_acc:
            best_acc = val_acc
            best_model_wts = copy.deepcopy(model.state_dict())
            torch.save(model.state_dict(), SAVE_PATH)
            print(f"✓ 最佳模型已保存 (Val Acc: {best_acc:.4f})")
    
    model.load_state_dict(best_model_wts)
    print(f"\n训练完成！最佳验证准确率: {best_acc:.4f}")
    return model

# ==================== 主函数 ====================
if __name__ == "__main__":
    print("=" * 50)
    print("灾害图像分类模型训练 (电脑/Colab 端)")
    print("=" * 50)
    
    train_loader, val_loader, class_names = load_datasets()
    model = create_model(NUM_CLASSES)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    # 可选: 学习率调度
    # scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)
    
    trained_model = train_model(model, train_loader, val_loader, criterion, optimizer, NUM_EPOCHS)
    
    print(f"\n模型已保存至: {SAVE_PATH}")
    print("下一步: 运行 export_to_tflite.py 转换模型")