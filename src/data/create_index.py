# python src/data/create_index.py

import os
import pandas as pd
from pathlib import Path

def create_dataset_index(raw_data_dir, output_csv):
    data = []
    base_path = Path(raw_data_dir)
    
    for seg_path in base_path.rglob("*-seg.nii.gz"):
        patient_dir = seg_path.parent
        prefix = seg_path.name.replace('-seg.nii.gz', '')
        files_in_dir = [f.name for f in patient_dir.iterdir() if f.is_file()]
        
        t1_file = next((f for f in files_in_dir if f.endswith('t1n.nii.gz')), None)
        t1c_file = next((f for f in files_in_dir if f.endswith('t1c.nii.gz')), None)
        t2_file = next((f for f in files_in_dir if f.endswith('t2w.nii.gz')), None)
        flair_file = next((f for f in files_in_dir if f.endswith('t2f.nii.gz')), None)

        if t1_file and t1c_file and t2_file and flair_file:
            paths = {
                'patient_id': prefix,
                't1': str(patient_dir / t1_file), 
                't1c': str(patient_dir / t1c_file),
                't2': str(patient_dir / t2_file),
                'flair': str(patient_dir / flair_file),
                'seg': str(seg_path)
            }
            data.append(paths)
            
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Індекс створено! Знайдено {len(df)} пацієнтів з повним набором даних. Збережено у {output_csv}")

if __name__ == "__main__":
    create_dataset_index("data/raw", "data/processed/dataset_index.csv")