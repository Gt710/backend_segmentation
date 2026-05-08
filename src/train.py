# import sys
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import torch
# import torch.nn as nn
# import torch.optim as optim
# from src.data.dataset import get_dataloaders
# from src.models.unet3d import UNet3D
# from tqdm import tqdm
# import time


# class DiceLoss(nn.Module):
#     def __init__(self, smooth=1.0):
#         super(DiceLoss, self).__init__()
#         self.smooth = smooth

#     def forward(self, preds, targets):
#         preds = preds.contiguous()
#         targets = targets.contiguous()
        
#         intersection = (preds * targets).sum(dim=(2, 3, 4))
#         dice = (2. * intersection + self.smooth) / (preds.sum(dim=(2, 3, 4)) + targets.sum(dim=(2, 3, 4)) + self.smooth)
        
#         return 1 - dice.mean()

# def train_model(epochs=30, batch_size=2, lr=0.001, resume=False):
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     print(f"Використовуємо пристрій: {device}")

#     # 1. Завантаження даних
#     train_loader, val_loader = get_dataloaders("data/processed/dataset_index.csv", batch_size=batch_size)

#     # 2. Ініціалізація моделі
#     model = UNet3D(in_channels=4, out_channels=1).to(device)
    
#     if resume and os.path.exists("models/unet3d_final.pth"):
#         model.load_state_dict(torch.load("models/unet3d_final.pth"))
#         print("Продовжуємо навчання з існуючих ваг...")
        
#     optimizer = optim.Adam(model.parameters(), lr=lr)
#     criterion = DiceLoss()

#     best_val_loss = float('inf')
#     os.makedirs("models", exist_ok=True)

#     # 3. Цикл навчання
#     for epoch in range(epochs):
#         epoch_start = time.time()
#         model.train()
#         train_loss = 0
        
#         # Прогрес-бар для тренування
#         train_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [Train]")
        
#         for images, masks in train_bar:
#             images = images.to(device)
#             masks = masks.to(device).float()
            
#             optimizer.zero_grad()
#             outputs = model(images)
#             loss = criterion(outputs, masks)
#             loss.backward()
#             optimizer.step()
            
#             train_loss += loss.item()
#             train_bar.set_postfix(loss=f"{loss.item():.4f}")
        
#         # Валідація
#         model.eval()
#         val_loss = 0
#         val_bar = tqdm(val_loader, desc=f"Epoch {epoch+1}/{epochs} [Val]")
        
#         with torch.no_grad():
#             for images, masks in val_bar:
#                 images = images.to(device)
#                 masks = masks.to(device).float()
#                 outputs = model(images)
#                 loss = criterion(outputs, masks)
#                 val_loss += loss.item()
#                 val_bar.set_postfix(loss=f"{loss.item():.4f}")
        
#         avg_train_loss = train_loss / len(train_loader)
#         avg_val_loss = val_loss / len(val_loader)
#         epoch_duration = time.time() - epoch_start
        
#         print(f"\nSummary Epoch {epoch+1}: Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} | Time: {epoch_duration:.1f}s")
        
#         # Зберігаємо найкращу модель
#         if avg_val_loss < best_val_loss:
#             best_val_loss = avg_val_loss
#             torch.save(model.state_dict(), "models/unet3d_best.pth")
#             print(f"  --> Нова найкраща модель збережена! (Val Loss: {best_val_loss:.4f})")

#     # Збереження фінальної моделі
#     torch.save(model.state_dict(), "models/unet3d_final.pth")
#     print("\nНавчання завершено.")
#     print("Найкраща модель: models/unet3d_best.pth")
#     print("Фінальна модель: models/unet3d_final.pth")

# if __name__ == "__main__":
#     train_model(epochs=30, resume=False)


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.amp import GradScaler, autocast
from torch.optim.lr_scheduler import ReduceLROnPlateau
from src.data.dataset import get_dataloaders
from src.models.unet3d import UNet3D
from tqdm import tqdm
import time
import torch.backends.cudnn as cudnn

cudnn.benchmark = True

class ComboLoss(nn.Module):
    def __init__(self, smooth=1.0):
        super(ComboLoss, self).__init__()
        self.smooth = smooth
        self.bce = nn.BCELoss()

    def forward(self, preds, targets):
        # BCE Loss
        bce_loss = self.bce(preds, targets)
        
        # Dice Loss
        preds = preds.contiguous()
        targets = targets.contiguous()
        intersection = (preds * targets).sum(dim=(2, 3, 4))
        dice = (2. * intersection + self.smooth) / (preds.sum(dim=(2, 3, 4)) + targets.sum(dim=(2, 3, 4)) + self.smooth)
        dice_loss = 1 - dice.mean()
        
        # Комбінація (80% Dice + 20% BCE)
        return bce_loss * 0.2 + dice_loss * 0.8

def train_model(epochs=100, batch_size=8, lr=0.0002, resume=True):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Використовуємо пристрій: {device}")

    train_loader, val_loader = get_dataloaders("data/processed/dataset_index.csv", batch_size=batch_size)

    model = UNet3D(in_channels=4, out_channels=1).to(device)
    
    if resume and os.path.exists("models/unet3d_final.pth"):
        model.load_state_dict(torch.load("models/unet3d_final.pth"))
        print("Продовжуємо навчання з існуючих ваг...")
        
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = ComboLoss()
    
    # Scheduler для зменшення learning rate
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
    
    # Mixed Precision Scaler для швидкості та економії пам'яті
    scaler = GradScaler('cuda')

    best_val_loss = float('inf')
    os.makedirs("models", exist_ok=True)

    for epoch in range(epochs):
        epoch_start = time.time()
        model.train()
        train_loss = 0
        
        train_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [Train]")
        
        for images, masks in train_bar:
            images = images.to(device)
            masks = masks.to(device).float()
            
            optimizer.zero_grad()
            
            # Автоматичне приведення типів (Mixed Precision)
            with autocast('cuda'):
                outputs = model(images)
            
            # Рахуємо лос поза autocast у float32, щоб уникнути помилки BCELoss
            loss = criterion(outputs.float(), masks.float())
            
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            
            train_loss += loss.item()
            train_bar.set_postfix(loss=f"{loss.item():.4f}")
        
        model.eval()
        val_loss = 0
        val_bar = tqdm(val_loader, desc=f"Epoch {epoch+1}/{epochs} [Val]")
        
        with torch.no_grad():
            for images, masks in val_bar:
                images = images.to(device)
                masks = masks.to(device).float()
                
                with autocast('cuda'):
                    outputs = model(images)
                
                loss = criterion(outputs.float(), masks.float())
                    
                val_loss += loss.item()
                val_bar.set_postfix(loss=f"{loss.item():.4f}")
        
        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)
        epoch_duration = time.time() - epoch_start
        
        print(f"\nSummary Epoch {epoch+1}: Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} | Time: {epoch_duration:.1f}s")
        
        # Крок планувальника (зменшення LR, якщо потрібно)
        scheduler.step(avg_val_loss)
        
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), "models/unet3d_best.pth")
            print(f"  --> Нова найкраща модель збережена! (Val Loss: {best_val_loss:.4f})")

    torch.save(model.state_dict(), "models/unet3d_final.pth")
    print("\nНавчання завершено.")

if __name__ == "__main__":
    train_model(epochs=100, resume=True)
