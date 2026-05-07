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