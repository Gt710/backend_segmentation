import os
from huggingface_hub import snapshot_download

def download_optimal_subset():
    repo_id = "Spirit-26/BraTS-2024-Complete"
    local_dir = "data/raw"
    
    os.makedirs(local_dir, exist_ok=True)
    
    print("Починаємо завантаження...")
    
    # Відбираємо рівно 600 пацієнтів (від 00000 до 00599 з категорії GLI)
    # Зірочка (*) потрібна, щоб врахувати структуру папок HuggingFace
    patterns = [
        "*GLI-000*", "*GLI-001*", "*GLI-002*", 
        "*GLI-003*", "*GLI-004*", "*GLI-005*"
    ]
    
    try:
        snapshot_download(
            repo_id=repo_id,
            repo_type="dataset",
            local_dir=local_dir,
            allow_patterns=patterns,
            max_workers=8
        )
        print("\nЗавантаження пацієнтів успішно завершено! Дані знаходяться у папці data/raw")
    except Exception as e:
        print(f"\nПомилка під час завантаження: {e}")

if __name__ == "__main__":
    download_optimal_subset()
