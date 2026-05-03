# python src/data/download_subset.py

import os
from huggingface_hub import snapshot_download

def download_brats_subset():
    repo_id = "Spirit-26/BraTS-2024-Complete"
    local_dir = "data/raw"
    
    os.makedirs(local_dir, exist_ok=True)
    
    print("Починаємо завантаження Dev-вибірки (збільшено до ~100 пацієнтів)...")
    
    subset_patterns = []
    # Завантажуємо перші 50 пацієнтів з GLI та 50 з MEN-RT
    for i in range(50):
        subset_patterns.append(f"BraTS-GLI/train/*-00{i:02d}*/*")
        subset_patterns.append(f"BraTS-MEN-RT/train/*-00{i:02d}*/*")
    
    try:
        snapshot_download(
            repo_id=repo_id,
            repo_type="dataset",
            local_dir=local_dir,
            allow_patterns=subset_patterns,
            max_workers=4
        )
        print("\nЗавантаження успішно завершено! Дані знаходяться у папці data/raw")
    except Exception as e:
        print(f"\nПомилка під час завантаження: {e}")

if __name__ == "__main__":
    download_brats_subset()