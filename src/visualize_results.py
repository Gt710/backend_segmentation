import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from src.models.unet3d import UNet3D
from src.data.dataset import BraTSDataset

def visualize_prediction(model_path, dataset_csv):
    # Визначаємо пристрій
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Використовуємо для візуалізації: {device}")
    
    # Завантаження моделі
    model = UNet3D(in_channels=4, out_channels=1).to(device)
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path))
        print(f"Модель завантажена з {model_path}")
    else:
        print("Помилка: Файл моделі не знайдено!")
        return

    model.eval()
    
    # Створюємо датасет (без випадкового обрізання, беремо центр)
    dataset = BraTSDataset(dataset_csv, patch_size=(128, 128, 128))
    
    # Беремо пацієнта (наприклад, 15-го)
    patient_idx = 118
    image, mask = dataset[patient_idx]
    
    input_tensor = image.unsqueeze(0).to(device)
    
    with torch.no_grad():
        prediction = model(input_tensor)
        prediction = (prediction > 0.5).float() # Поріг для бінарної маски
    
    print(f"Унікальні значення в масці лікаря: {np.unique(mask.numpy())}")
    print(f"Унікальні значення в прогнозі ШІ: {np.unique(prediction.cpu().numpy())}")

    # Вибираємо центральний зріз для візуалізації
    slice_idx = 64
    
    # Конвертуємо в numpy
    img_np = image[3, :, :, slice_idx].cpu().numpy() # FLAIR
    mask_np = mask[0, :, :, slice_idx].cpu().numpy()
    pred_np = prediction[0, 0, :, :, slice_idx].cpu().numpy()
    
    # Створюємо графік
    plt.figure(figsize=(18, 6))
    
    plt.subplot(1, 3, 1)
    plt.title(f"МРТ (FLAIR) - Пацієнт {patient_idx}")
    plt.imshow(img_np, cmap='gray')
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.title("Еталонна маска (Лікар)")
    plt.imshow(img_np, cmap='gray')
    plt.imshow(mask_np, cmap='jet', alpha=0.5) # Накладаємо маску поверх
    plt.axis('off')
    
    plt.subplot(1, 3, 3)
    plt.title("Прогноз нейромережі")
    plt.imshow(img_np, cmap='gray')
    plt.imshow(pred_np, cmap='jet', alpha=0.5) # Накладаємо прогноз поверх
    plt.axis('off')
    
    plt.tight_layout()
    print("Відображаємо результат...")
    plt.show()

if __name__ == "__main__":
    # Використовуємо найкращу модель
    visualize_prediction("models/unet3d_best.pth", "data/processed/dataset_index.csv")
