import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn as nn
import torch.optim as optim
from src.data.dataset import get_dataloaders
from src.models.unet3d import UNet3D


class DiceLoss(nn.Module):
    def __init__(self, smooth=1.0):
        super(DiceLoss, self).__init__()
        self.smooth = smooth

    def forward(self, preds, targets):
        preds = preds.contiguous()
        targets = targets.contiguous()
        
        intersection = (preds * targets).sum(dim=(2, 3, 4))
        dice = (2. * intersection + self.smooth) / (preds.sum(dim=(2, 3, 4)) + targets.sum(dim=(2, 3, 4)) + self.smooth)
        
        return 1 - dice.mean()

def train_model(epochs=10, batch_size=2, lr=0.001):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Використовуємо пристрій: {device}")

    # 1. Завантаження даних
    train_loader, val_loader = get_dataloaders("data/processed/dataset_index.csv", batch_size=batch_size)

    # 2. Ініціалізація моделі
    model = UNet3D(in_channels=4, out_channels=1).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = DiceLoss()

    # 3. Цикл навчання
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for images, masks in train_loader:
            images = images.to(device)
            masks = masks.to(device).float()
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, masks)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        # Валідація
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for images, masks in val_loader:
                images = images.to(device)
                masks = masks.to(device).float()
                outputs = model(images)
                loss = criterion(outputs, masks)
                val_loss += loss.item()
        
        print(f"Epoch {epoch+1}/{epochs} | Train Loss: {train_loss/len(train_loader):.4f} | Val Loss: {val_loss/len(val_loader):.4f}")

    # Збереження моделі
    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/unet3d_final.pth")
    print("Навчання завершено. Модель збережено у models/unet3d_final.pth")

if __name__ == "__main__":
    train_model(epochs=5) # Для тесту ставимо 5 епох
