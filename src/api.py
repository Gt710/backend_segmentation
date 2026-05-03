import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, File, UploadFile
import torch
import nibabel as nib
import numpy as np
from src.models.unet3d import UNet3D
from src.data.preprocessing import get_bounding_box, crop_volume, normalize_intensity
import io

app = FastAPI(title="Segmentation Model API")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = UNet3D(in_channels=4, out_channels=1).to(device)
model_path = "models/unet3d_final.pth"

if os.path.exists(model_path):
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    print("Модель успішно завантажена!")
else:
    print("Попередження: Файл моделі не знайдено.")

@app.post("/predict")
async def predict(t1: UploadFile = File(...), t1c: UploadFile = File(...), t2: UploadFile = File(...), flair: UploadFile = File(...)):
    
    return {"status": "success", "message": "Зображення отримано. Тут буде результат сегментації."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
