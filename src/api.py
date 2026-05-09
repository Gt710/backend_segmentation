import os
import sys
import shutil
import tempfile
import io
import base64
import numpy as np
import torch
import nibabel as nib
import matplotlib.pyplot as plt
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Реєструємо шрифти з підтримкою кирилиці
try:
    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
except Exception as e:
    print(f"Попередження: Не вдалося завантажити шрифти Arial: {e}")

from src.models.unet3d import UNet3D
from src.data.preprocessing import get_bounding_box, crop_volume, normalize_intensity

app = FastAPI(title="Brain Tumor Segmentation API")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = UNet3D(in_channels=4, out_channels=1).to(device)
model_path = "models/unet3d_best.pth"

if os.path.exists(model_path):
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    print(f"Модель успішно завантажена з {model_path}")
else:
    print(f"Попередження: Файл моделі не знайдено за шляхом {model_path}")

def generate_pdf_report(volume, conclusion, slices_images):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Arial-Bold',
        fontSize=20,
        textColor=colors.HexColor('#2C3E50'),
        alignment=1,
        spaceAfter=12
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=12,
        spaceAfter=6
    )
    
    story.append(Paragraph("Звіт про аналіз МРТ знімків", title_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"<b>Об'єм пухлини:</b> {volume:.2f} см³", normal_style))
    story.append(Paragraph(f"<b>Висновок:</b> {conclusion}", normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Візуалізація зрізів (FLAIR + Маска):</b>", normal_style))
    story.append(Spacer(1, 6))
    
    table_data = []
    row = []
    for i, img_buf in enumerate(slices_images):
        img = Image(img_buf, width=150, height=150)
        row.append(img)
        if len(row) == 3:
            table_data.append(row)
            row = []
    if row:
        while len(row) < 3:
            row.append("")
        table_data.append(row)
        
    t = Table(table_data, colWidths=[180, 180, 180])
    t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.read()

@app.post("/predict")
async def predict(
    t1: UploadFile = File(...), 
    t1c: UploadFile = File(...), 
    t2: UploadFile = File(...), 
    flair: UploadFile = File(...)
):
    with tempfile.TemporaryDirectory() as temp_dir:
        t1_path = os.path.join(temp_dir, "t1.nii.gz")
        t1c_path = os.path.join(temp_dir, "t1c.nii.gz")
        t2_path = os.path.join(temp_dir, "t2.nii.gz")
        flair_path = os.path.join(temp_dir, "flair.nii.gz")
        
        with open(t1_path, "wb") as buffer:
            shutil.copyfileobj(t1.file, buffer)
        with open(t1c_path, "wb") as buffer:
            shutil.copyfileobj(t1c.file, buffer)
        with open(t2_path, "wb") as buffer:
            shutil.copyfileobj(t2.file, buffer)
        with open(flair_path, "wb") as buffer:
            shutil.copyfileobj(flair.file, buffer)
            
        t1_img = nib.load(t1_path)
        t1_data = t1_img.get_fdata().astype(np.float32)
        t1c_data = nib.load(t1c_path).get_fdata().astype(np.float32)
        t2_data = nib.load(t2_path).get_fdata().astype(np.float32)
        flair_img = nib.load(flair_path)
        flair_data = flair_img.get_fdata().astype(np.float32)
        
        header = flair_img.header
        pixdim = header['pixdim']
        voxel_volume_mm3 = pixdim[1] * pixdim[2] * pixdim[3]
        
        min_c, max_c = get_bounding_box(flair_data)
        
        t1_cropped = crop_volume(t1_data, min_c, max_c)
        t1c_cropped = crop_volume(t1c_data, min_c, max_c)
        t2_cropped = crop_volume(t2_data, min_c, max_c)
        flair_cropped = crop_volume(flair_data, min_c, max_c)
        
        t1_norm = normalize_intensity(t1_cropped)
        t1c_norm = normalize_intensity(t1c_cropped)
        t2_norm = normalize_intensity(t2_cropped)
        flair_norm = normalize_intensity(flair_cropped)
        
        image_volume = np.stack([t1_norm, t1c_norm, t2_norm, flair_norm], axis=0)
        
        c, h, w, d = image_volume.shape
        ph, pw, pd = h, w, d
        if h % 4 != 0: ph = ((h // 4) + 1) * 4
        if w % 4 != 0: pw = ((w // 4) + 1) * 4
        if d % 4 != 0: pd = ((d // 4) + 1) * 4
        
        if ph != h or pw != w or pd != d:
            pad_width = [(0, 0), (0, ph - h), (0, pw - w), (0, pd - d)]
            image_volume = np.pad(image_volume, pad_width, mode='constant')
            
        input_tensor = torch.from_numpy(image_volume).unsqueeze(0).to(device)
        
        with torch.no_grad():
            prediction = model(input_tensor)
            prediction = (prediction > 0.5).float()
            
        pred_np = prediction[0, 0, :h, :w, :d].cpu().numpy()
        
        tumor_voxel_count = np.sum(pred_np)
        volume_cm3 = (tumor_voxel_count * voxel_volume_mm3) / 1000.0
        
        if volume_cm3 == 0:
            conclusion = "Пухлину не виявлено або її об'єм занадто малий."
        elif volume_cm3 < 10:
            conclusion = "Малий об'єм пухлини. Рекомендовано регулярне спостереження."
        elif volume_cm3 < 50:
            conclusion = "Середній об'єм пухлини. Необхідна консультація онколога та додаткові обстеження."
        else:
            conclusion = "Великий об'єм пухлини. Потрібне термінове медичне втручання."
            
        slices_images = []
        tumor_slices = np.where(np.sum(pred_np, axis=(0, 1)) > 0)[0]
        
        if len(tumor_slices) > 0:
            start_slice = tumor_slices[0]
            end_slice = tumor_slices[-1]
            selected_slices = np.linspace(start_slice, end_slice, min(30, len(tumor_slices)), dtype=int)
        else:
            selected_slices = np.linspace(0, d - 1, min(30, d), dtype=int)
            
        for s_idx in selected_slices:
            img_slice = flair_cropped[:, :, s_idx]
            pred_slice = pred_np[:, :, s_idx]
            
            fig, ax = plt.subplots(figsize=(3, 3))
            ax.imshow(img_slice, cmap='gray')
            if np.sum(pred_slice) > 0:
                ax.imshow(pred_slice, cmap='jet', alpha=0.5)
            ax.axis('off')
            ax.set_title(f"Зріз {s_idx}", fontsize=8)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            slices_images.append(buf)
            plt.close(fig)
            
        pdf_bytes = generate_pdf_report(volume_cm3, conclusion, slices_images)
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return {
            "status": "success",
            "volume_cm3": float(volume_cm3),
            "conclusion": conclusion,
            "pdf_report_base64": pdf_base64
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
