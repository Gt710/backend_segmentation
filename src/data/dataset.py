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
        seg = nib.load(patient['seg']).get_fdata()
        
        # КРИТИЧНО: Бінаризація маски (Whole Tumor)
        seg = (seg > 0).astype(np.float32) 
        
        min_c, max_c = get_bounding_box(flair)
        
        t1 = crop_volume(t1, min_c, max_c)
        t1c = crop_volume(t1c, min_c, max_c)
        t2 = crop_volume(t2, min_c, max_c)
        flair = crop_volume(flair, min_c, max_c)
        seg = crop_volume(seg, min_c, max_c)

        # ДОДАНО: Перевірка на мінімальний розмір (Padding)
        h, w, d = t1.shape
        ph, pw, pd_size = self.patch_size
        
        if h < ph or w < pw or d < pd_size:
            pad_h = max(0, ph - h)
            pad_w = max(0, pw - w)
            pad_d = max(0, pd_size - d)
            pad_width = [(0, pad_h), (0, pad_w), (0, pad_d)]
            
            t1 = np.pad(t1, pad_width, mode='constant')
            t1c = np.pad(t1c, pad_width, mode='constant')
            t2 = np.pad(t2, pad_width, mode='constant')
            flair = np.pad(flair, pad_width, mode='constant')
            seg = np.pad(seg, pad_width, mode='constant')

        t1 = normalize_intensity(t1)
        t1c = normalize_intensity(t1c)
        t2 = normalize_intensity(t2)
        flair = normalize_intensity(flair)
        
        image_volume = np.stack([t1, t1c, t2, flair], axis=0)
        
        _, h, w, d = image_volume.shape
        
        # Balanced Sampling: 50% ймовірність взяти патч із пухлиною
        if np.random.rand() > 0.5 and np.sum(seg) > 0:
            # Знаходимо всі координати, де є пухлина
            tumor_coords = np.argwhere(seg > 0)
            # Вибираємо випадковий піксель пухлини як центр патча
            center_h, center_w, center_d = tumor_coords[np.random.randint(0, len(tumor_coords))]
            
            # Зміщуємо координати старту, щоб цей піксель був десь по центру патча
            start_h = max(0, min(center_h - ph // 2, h - ph))
            start_w = max(0, min(center_w - pw // 2, w - pw))
            start_d = max(0, min(center_d - pd_size // 2, d - pd_size))
        else:
            # Звичайний випадковий патч (max(1, ...) щоб уникнути помилок якщо розміри рівні)
            start_h = np.random.randint(0, max(1, h - ph))
            start_w = np.random.randint(0, max(1, w - pw))
            start_d = np.random.randint(0, max(1, d - pd_size))
        
        img_patch = image_volume[:, start_h:start_h+ph, start_w:start_w+pw, start_d:start_d+pd_size]
        mask_patch = seg[np.newaxis, start_h:start_h+ph, start_w:start_w+pw, start_d:start_d+pd_size]
        
        # Data Augmentation: Випадкове віддзеркалення (без впливу на час завантаження)
        if np.random.rand() > 0.5:
            img_patch = np.flip(img_patch, axis=2)
            mask_patch = np.flip(mask_patch, axis=2)
        if np.random.rand() > 0.5:
            img_patch = np.flip(img_patch, axis=3)
            mask_patch = np.flip(mask_patch, axis=3)
            
        # .copy() потрібен, оскільки PyTorch не любить віддзеркалені numpy-масиви
        return torch.from_numpy(img_patch.copy()), torch.from_numpy(mask_patch.copy())

def get_dataloaders(csv_file, batch_size=2, patch_size=(64, 64, 64), val_split=0.2):
    from torch.utils.data import DataLoader, random_split
    
    full_dataset = BraTSDataset(csv_file, patch_size)
    val_size = int(len(full_dataset) * val_split)
    train_size = len(full_dataset) - val_size
    
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True, persistent_workers=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True, persistent_workers=True)
    
    return train_loader, val_loader