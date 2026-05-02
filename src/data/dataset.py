# python -m src.data.dataset

import torch
from torch.utils.data import Dataset
import nibabel as nib
import pandas as pd
import numpy as np
from src.data.preprocessing import get_bounding_box, crop_volume, normalize_intensity

class BraTSDataset(Dataset):
    def __init__(self, csv_file, patch_size=(64, 64, 64)):
        self.data_index = pd.read_csv(csv_file)
        self.patch_size = patch_size

    def __len__(self):
        return len(self.data_index)

    def __getitem__(self, idx):
        patient = self.data_index.iloc[idx]
        
        t1 = nib.load(patient['t1']).get_fdata().astype(np.float32)
        t1c = nib.load(patient['t1c']).get_fdata().astype(np.float32)
        t2 = nib.load(patient['t2']).get_fdata().astype(np.float32)
        flair = nib.load(patient['flair']).get_fdata().astype(np.float32)
        seg = nib.load(patient['seg']).get_fdata().astype(np.uint8) 
        
        min_c, max_c = get_bounding_box(flair)
        
        t1 = crop_volume(t1, min_c, max_c)
        t1c = crop_volume(t1c, min_c, max_c)
        t2 = crop_volume(t2, min_c, max_c)
        flair = crop_volume(flair, min_c, max_c)
        seg = crop_volume(seg, min_c, max_c)
        
        t1 = normalize_intensity(t1)
        t1c = normalize_intensity(t1c)
        t2 = normalize_intensity(t2)
        flair = normalize_intensity(flair)
        
        image_volume = np.stack([t1, t1c, t2, flair], axis=0)
        
        ph, pw, pd_size = self.patch_size
        _, h, w, d = image_volume.shape
        
        start_h = np.random.randint(0, h - ph)
        start_w = np.random.randint(0, w - pw)
        start_d = np.random.randint(0, d - pd_size)
        
        img_patch = image_volume[:, start_h:start_h+ph, start_w:start_w+pw, start_d:start_d+pd_size]
        mask_patch = seg[np.newaxis, start_h:start_h+ph, start_w:start_w+pw, start_d:start_d+pd_size]
        
        return torch.from_numpy(img_patch), torch.from_numpy(mask_patch)

if __name__ == "__main__":
    print("Тестуємо PyTorch Dataset...")
    dataset = BraTSDataset("data/processed/dataset_index.csv", patch_size=(64, 64, 64))
    img_tensor, mask_tensor = dataset[0]
    
    print(f"Формат вхідного тензора (зображення): {img_tensor.shape} (Має бути: 4, 64, 64, 64)")
    print(f"Формат вихідного тензора (маска): {mask_tensor.shape} (Має бути: 1, 64, 64, 64)")
    print(f"Тип даних маски: {mask_tensor.dtype}")