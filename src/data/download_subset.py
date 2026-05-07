# # python src/data/download_subset.py

# import os
# from huggingface_hub import snapshot_download

# def download_brats_subset():
#     repo_id = "Spirit-26/BraTS-2024-Complete"
#     local_dir = "data/raw"
    
#     os.makedirs(local_dir, exist_ok=True)
    
#     print("Починаємо завантаження половини датасету (~1364 пацієнтів)...")
    
#     subset_patterns = []
#     # 1. GLI: перші 900 пацієнтів (ID 00000-00899)
#     for i in range(90): 
#         subset_patterns.append(f"BraTS-GLI/train/*-00{i:02d}*/*")
    
#     # 2. MEN-RT: перші 300 пацієнтів (ID 00000-00299)
#     for i in range(30):
#         subset_patterns.append(f"BraTS-MEN-RT/train/*-00{i:02d}*/*")
        
#     # 3. PED: перші 164 пацієнти (ID 00000-00163)
#     for i in range(17):
#         subset_patterns.append(f"BraTS-PED/train/*-00{i:02d}*/*")
    
#     try:
#         snapshot_download(
#             repo_id=repo_id,
#             repo_type="dataset",
#             local_dir=local_dir,
#             allow_patterns=subset_patterns,
#             max_workers=4
#         )
#         print("\nЗавантаження успішно завершено! Дані знаходяться у папці data/raw")
#     except Exception as e:
#         print(f"\nПомилка під час завантаження: {e}")

# if __name__ == "__main__":
#     download_brats_subset()


import os
from huggingface_hub import snapshot_download

def download_full_brats():
    repo_id = "Spirit-26/BraTS-2024-Complete"
    local_dir = "data/raw"
    
    os.makedirs(local_dir, exist_ok=True)
    
    print("Починаємо завантаження ПОВНОГО датасету...")
    
    try:
        # Якщо allow_patterns не вказано, завантажиться весь репозиторій
        snapshot_download(
            repo_id=repo_id,
            repo_type="dataset",
            local_dir=local_dir,
            max_workers=8 # Збільшено кількість потоків для швидкості
        )
        print("\nЗавантаження успішно завершено! Дані знаходяться у папці data/raw")
    except Exception as e:
        print(f"\nПомилка під час завантаження: {e}")

if __name__ == "__main__":
    download_full_brats()
