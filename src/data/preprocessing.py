# python src/data/preprocessing.py

import numpy as np

def get_bounding_box(image_data):
    coords = np.array(np.nonzero(image_data > 0))
    min_coords = coords.min(axis=1)
    max_coords = coords.max(axis=1) + 1
    
    return min_coords, max_coords

def crop_volume(image_data, min_coords, max_coords):
    return image_data[
        min_coords[0]:max_coords[0],
        min_coords[1]:max_coords[1],
        min_coords[2]:max_coords[2]
    ]

def normalize_intensity(image_data):
    brain_mask = image_data > 0
    brain_pixels = image_data[brain_mask]
    
    mean = np.mean(brain_pixels)
    std = np.std(brain_pixels)
    
    normalized_data = np.zeros_like(image_data, dtype=np.float32)
    
    if std > 0:
        normalized_data[brain_mask] = (image_data[brain_mask] - mean) / std
        
    return normalized_data


if __name__ == "__main__":
    import pandas as pd
    import nibabel as nib
    
    print("Тестуємо попередню обробку...")
    
    df = pd.read_csv("data/processed/dataset_index.csv")
    patient = df.iloc[0]
    
    flair_data = nib.load(patient['flair']).get_fdata()
    
    print(f"\nДО ОБРОБКИ:")
    print(f"Розмірність масиву: {flair_data.shape}")
    print(f"Пам'ять, яку займає масив: {flair_data.nbytes / (1024*1024):.2f} МБ")
    print(f"Мінімальне значення пікселя: {flair_data.min()}, Максимальне: {flair_data.max():.2f}")
    
    min_c, max_c = get_bounding_box(flair_data)
    cropped_flair = crop_volume(flair_data, min_c, max_c)
    
    processed_flair = normalize_intensity(cropped_flair)
    
    print(f"\nПІСЛЯ ОБРОБКИ:")
    print(f"Нова розмірність (без фону): {processed_flair.shape}")
    print(f"Новий об'єм пам'яті: {processed_flair.nbytes / (1024*1024):.2f} МБ")
    print(f"Мінімум: {processed_flair.min():.2f}, Максимум: {processed_flair.max():.2f}")
    
    brain_pixels_after = processed_flair[processed_flair != 0]
    print(f"Середнє значення тканин мозку (має бути ~0): {brain_pixels_after.mean():.4f}")
    print(f"Стандартне відхилення (має бути ~1): {brain_pixels_after.std():.4f}")


    import matplotlib.pyplot as plt

    original_slice_idx = flair_data.shape[2] // 2
    processed_slice_idx = processed_flair.shape[2] // 2
    
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.title('ДО (Оригінал з фоном)')
    plt.imshow(flair_data[:, :, original_slice_idx], cmap='gray')
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.title('ПІСЛЯ (Обрізано + Нормалізовано)')
    plt.imshow(processed_flair[:, :, processed_slice_idx], cmap='gray')
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()