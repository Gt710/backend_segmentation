# python notebooks/explore_data.py

import pandas as pd
import nibabel as nib
import matplotlib.pyplot as plt

def visualize_mri_slice():
    try:
        df = pd.read_csv("data/processed/dataset_index.csv")
        if df.empty:
            print("CSV файл порожній. Перевірте скрипт індексації.")
            return
    except FileNotFoundError:
        print("Файл dataset_index.csv не знайдено.")
        return
    patient = df.iloc[0]
    
    print(f"Візуалізуємо пацієнта: {patient['patient_id']}")
    
    flair_img = nib.load(patient['flair'])
    seg_img = nib.load(patient['seg'])
    
    flair_data = flair_img.get_fdata()
    seg_data = seg_img.get_fdata()
    
    print(f"Розмірність 3D МРТ-знімка: {flair_data.shape}")
    
    # slice_idx = 75
    tumor_pixels_per_slice = (seg_data > 0).sum(axis=(0, 1)) 
    
    best_slice_idx = tumor_pixels_per_slice.argmax()
    
    print(f"Найкращий зріз з пухлиною: {best_slice_idx}")
    
    slice_idx = best_slice_idx 
    
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.title(f'МРТ (FLAIR) - Зріз {slice_idx}')
    plt.imshow(flair_data[:, :, slice_idx], cmap='gray')
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.title(f'Маска пухлини (Розмітка) - Зріз {slice_idx}')
    plt.imshow(seg_data[:, :, slice_idx], cmap='nipy_spectral', vmin=0, vmax=4)
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize_mri_slice()