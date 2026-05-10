import os
import sys
import shutil
import tempfile
import io
import base64
import glob
import hashlib
import hmac
import numpy as np
import torch
import nibabel as nib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import scipy.ndimage as ndimage
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.unet3d import UNet3D
from src.data.preprocessing import get_bounding_box, crop_volume, normalize_intensity
from src.database import get_db, init_db, Patient, Scan, User, Log

app = FastAPI(title="Brain Tumor Segmentation API with Security")

# Ініціалізація БД
init_db()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = UNet3D(in_channels=4, out_channels=1).to(device)
model_path = "models/unet3d_best.pth"

if os.path.exists(model_path):
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    print(f"Модель успішно завантажена з {model_path}")
else:
    print(f"Попередження: Файл моделі не знайдено за шляхом {model_path}")

# Реєструємо шрифти з підтримкою кирилиці
try:
    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
except Exception as e:
    print(f"Попередження: Не вдалося завантажити шрифти Arial: {e}")

# --- ЗАСОБИ БЕЗПЕКИ ---

# 1. Хешування паролів (PBKDF2)
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return base64.b64encode(salt + pwd_hash).decode('utf-8')

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        data = base64.b64decode(stored_hash.encode('utf-8'))
        salt = data[:16]
        stored_pwd_hash = data[16:]
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return hmac.compare_digest(stored_pwd_hash, new_hash)
    except:
        return False

# 2. Шифрування полів БД (XOR + Base64 - Спрощена реалізація для диплому)
# У реальному проекті використовуйте cryptography.fernet
SECRET_KEY = "diploma_secret_key_123"

def encrypt_field(data: str) -> str:
    if not data: return data
    xor_data = "".join(chr(ord(c) ^ ord(SECRET_KEY[i % len(SECRET_KEY)])) for i, c in enumerate(data))
    return base64.b64encode(xor_data.encode('utf-8')).decode('utf-8')

def decrypt_field(encoded_data: str) -> str:
    if not encoded_data: return encoded_data
    try:
        data = base64.b64decode(encoded_data.encode('utf-8')).decode('utf-8')
        return "".join(chr(ord(c) ^ ord(SECRET_KEY[i % len(SECRET_KEY)])) for i, c in enumerate(data))
    except:
        return encoded_data

# 3. Хеш-ланцюжки для логів
def add_secure_log(message: str, db: Session):
    last_log = db.query(Log).order_by(Log.id.desc()).first()
    prev_hash = last_log.current_hash if last_log else "0" * 64
    
    data_to_hash = f"{message}{prev_hash}"
    current_hash = hashlib.sha256(data_to_hash.encode('utf-8')).hexdigest()
    
    log = Log(message=message, previous_hash=prev_hash, current_hash=current_hash)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

# 4. Захист ШІ від атак (Spatial Smoothing)
def apply_spatial_smoothing(image_volume):
    # Застосовуємо Гауссів фільтр для розмиття (згладжування)
    smoothed = np.zeros_like(image_volume)
    for c in range(image_volume.shape[0]):
        smoothed[c] = ndimage.gaussian_filter(image_volume[c], sigma=0.5)
    return smoothed

# 5. Рольова модель (RBAC) - Депенденсі
def get_current_user(username: str = Header(None), db: Session = Depends(get_db)):
    if not username:
        raise HTTPException(status_code=401, detail="Потрібна авторизація (передайте заголовок username)")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Користувача не знайдено")
    return user

def require_role(role: str):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != role and user.role != "Admin": # Адмін може все
            raise HTTPException(status_code=403, detail="Недостатньо прав доступу")
        return user
    return role_checker

# Створення демо-користувачів
@app.on_event("startup")
def create_demo_users():
    db = next(get_db())
    if not db.query(User).filter(User.username == "admin").first():
        admin = User(username="admin", password_hash=hash_password("admin123"), role="Admin")
        doctor = User(username="doctor", password_hash=hash_password("doctor123"), role="Radiologist")
        db.add(admin)
        db.add(doctor)
        db.commit()
        print("Демо-користувачі створені: admin/admin123, doctor/doctor123")

# --- КІНЕЦЬ ЗАСОБІВ БЕЗПЕКИ ---

def generate_pdf_report(volume, conclusion, slices_images, patient=None, tumor_nature="Недостатньо даних"):
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
    
    if patient:
        # Розшифровуємо дані для звіту
        f_name = decrypt_field(patient.first_name)
        l_name = decrypt_field(patient.last_name)
        phone = decrypt_field(patient.phone)
        
        story.append(Paragraph(f"<b>Пацієнт:</b> {f_name} {l_name}", normal_style))
        story.append(Paragraph(f"<b>Дата народження:</b> {patient.dob}", normal_style))
        story.append(Paragraph(f"<b>Телефон:</b> {phone}", normal_style))
        if patient.notes:
            story.append(Paragraph(f"<b>Нотатки:</b> {patient.notes}", normal_style))
        story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Тип пухлини:</b> Гліома", normal_style))
    story.append(Paragraph(f"<b>Характер (динаміка):</b> {tumor_nature}", normal_style))
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

# Ендпоінти
@app.get("/patients")
def get_patients(db: Session = Depends(get_db), current_user: User = Depends(require_role("Radiologist"))):
    patients = db.query(Patient).all()
    
    results = []
    for p in patients:
        results.append({
            "id": p.id,
            "first_name": decrypt_field(p.first_name),
            "last_name": decrypt_field(p.last_name),
            "dob": p.dob,
            "phone": decrypt_field(p.phone),
            "notes": p.notes,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "scans": [
                {
                    "id": s.id,
                    "status": s.status,
                    "upload_date": s.created_at.isoformat() if s.created_at else None,
                    "tumor_volume_cm3": s.tumor_volume_cm3,
                    "conclusion": s.conclusion
                } for s in p.scans
            ]
        })
    
    add_secure_log(f"Користувач {current_user.username} переглянув список пацієнтів", db)
    return results


@app.post("/patients")
def create_patient(first_name: str, last_name: str, dob: str, phone: str, notes: str = None, 
                   db: Session = Depends(get_db), current_user: User = Depends(require_role("Radiologist"))):
    # Шифруємо чутливі дані перед збереженням
    enc_first_name = encrypt_field(first_name)
    enc_last_name = encrypt_field(last_name)
    enc_phone = encrypt_field(phone)
    
    patient = Patient(first_name=enc_first_name, last_name=enc_last_name, dob=dob, phone=enc_phone, notes=notes)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    add_secure_log(f"Користувач {current_user.username} створив пацієнта ID {patient.id}", db)
    
    return {
        "id": patient.id,
        "first_name": first_name,
        "last_name": last_name,
        "dob": dob,
        "phone": phone,
        "notes": notes,
        "created_at": patient.created_at.isoformat() if patient.created_at else None
    }
    

@app.post("/analyze")
async def analyze_scan(
    patient_id: int,
    scan_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Radiologist"))
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Пацієнта не знайдено")
        
    # Пошук файлів на сервері (Ізоляція/Валідація)
    base_dir = "data/raw/BraTS-GLI/train"
    pattern = os.path.join(base_dir, f"BraTS-GLI-{scan_number}-*")
    folders = glob.glob(pattern)
    
    if not folders:
        raise HTTPException(status_code=404, detail=f"Папку для пацієнта BraTS-GLI-{scan_number} не знайдено")
        
    patient_dir = folders[0]
    
    try:
        # Валідація розширень
        t1_files = glob.glob(os.path.join(patient_dir, "*-t1n.nii.gz"))
        t1c_files = glob.glob(os.path.join(patient_dir, "*-t1c.nii.gz"))
        t2_files = glob.glob(os.path.join(patient_dir, "*-t2w.nii.gz"))
        flair_files = glob.glob(os.path.join(patient_dir, "*-t2f.nii.gz"))
        
        if not (t1_files and t1c_files and t2_files and flair_files):
            raise HTTPException(status_code=404, detail="Не всі модальності знайдено")
            
        t1_path = t1_files[0]
        t1c_path = t1c_files[0]
        t2_path = t2_files[0]
        flair_path = flair_files[0]
        
        # Завантаження (з обробкою помилок)
        t1_img = nib.load(t1_path)
        t1_data = t1_img.get_fdata().astype(np.float32)
        t1c_data = nib.load(t1c_path).get_fdata().astype(np.float32)
        t2_data = nib.load(t2_path).get_fdata().astype(np.float32)
        flair_img = nib.load(flair_path)
        flair_data = flair_img.get_fdata().astype(np.float32)
        
    except Exception as e:
        add_secure_log(f"Помилка парсингу файлів для пацієнта {scan_number}: {str(e)}", db)
        raise HTTPException(status_code=500, detail=f"Помилка обробки медичних файлів: {str(e)}")
        
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
    
    # ЗАХИСТ ШІ: Spatial Smoothing
    image_volume = apply_spatial_smoothing(image_volume)
    
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
        conclusion = "Відсутність макроскопічної пухлини. Пухлина не візуалізується. Може відповідати стану після повного видалення або повної ремісії."
    elif volume_cm3 < 15:
        conclusion = "Малий об'єм. Характерно для ранніх стадій або низькодиференційованих гліом (WHO Grade 1-2). Часто дозволяє провести радикальне видалення з мінімальним ризиком дефіциту."
    elif volume_cm3 < 40:
        conclusion = "Середній об'єм. Пухлина стає клінічно значущою. Можлива поява судомного синдрому або осередкової симптоматики. Вимагає активного лікування (хірургія + променева терапія)."
    elif volume_cm3 < 70:
        conclusion = "Значний об'єм. Високий ризик перифокального набряку та мас-ефекту. Потребує дексаметазонової підтримки та планування циторедуктивної операції."
    else:
        conclusion = "Критичний (гігантський) об'єм. Предиктор несприятливого прогнозу. Високий ризик дислокації мозку та вклинення. Необхідне термінове декомпресивне втручання."
        
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
        
    # Прогнозування типу пухлини (доброякісна/злоякісна) на основі історії
    previous_scans = db.query(Scan).filter(Scan.patient_id == patient.id, Scan.status == "completed").order_by(Scan.created_at.desc()).all()
    
    tumor_nature = "Недостатньо даних"
    if previous_scans:
        last_scan = previous_scans[0]
        diff = volume_cm3 - last_scan.tumor_volume_cm3
        if diff > 0:
            tumor_nature = f"Злоякісна (прогресування). Об'єм збільшився на {diff:.2f} см³"
        elif diff < 0:
            tumor_nature = f"Доброякісна або регресія. Об'єм зменшився на {abs(diff):.2f} см³"
        else:
            tumor_nature = "Стабільний стан (без змін)"
            
    pdf_bytes = generate_pdf_report(volume_cm3, conclusion, slices_images, patient, tumor_nature)
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    
    scan = Scan(
        patient_id=patient.id,
        scan_number=scan_number,
        status="completed",
        tumor_volume_cm3=float(volume_cm3),
        conclusion=conclusion,
        tumor_nature=tumor_nature
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    
    # Зберігаємо маску та звіт на диск для ендпоінтів
    os.makedirs("data/processed", exist_ok=True)
    
    # Створюємо повнорозмірну маску, щоб вона співпадала з оригінальним зображенням
    full_mask = np.zeros(flair_data.shape, dtype=np.float32)
    full_mask[min_c[0]:min_c[0]+h, min_c[1]:min_c[1]+w, min_c[2]:min_c[2]+d] = pred_np

    
    np.save(f"data/processed/mask_{scan.id}.npy", full_mask)
    with open(f"data/processed/report_{scan.id}.pdf", "wb") as f:
        f.write(pdf_bytes)



    
    add_secure_log(f"Користувач {current_user.username} провів аналіз для пацієнта ID {patient.id}. Об'єм: {volume_cm3:.2f} см³", db)
    
    return {
        "status": "success",
        "patient": {
            "id": patient.id,
            "first_name": decrypt_field(patient.first_name),
            "last_name": decrypt_field(patient.last_name),
            "dob": patient.dob,
            "notes": patient.notes,
            "created_at": patient.created_at.isoformat(),
            "scans": [
                {
                    "id": scan.id,
                    "status": scan.status,
                    "tumor_volume_cm3": scan.tumor_volume_cm3,
                    "conclusion": scan.conclusion,
                    "tumor_type": "Гліома",
                    "tumor_nature": scan.tumor_nature
                }
            ]
        },
        "pdf_report_base64": pdf_base64
    }
@app.get("/scans/{scan_id}/slice/{slice_idx}")
def get_scan_slice(scan_id: int, slice_idx: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    # Find files based on scan_number
    base_dir = "data/raw/BraTS-GLI/train"
    pattern = os.path.join(base_dir, f"BraTS-GLI-{scan.scan_number}-*")
    folders = glob.glob(pattern)
    
    if not folders:
        raise HTTPException(status_code=404, detail="Files not found for this scan")
        
    patient_dir = folders[0]
    flair_files = glob.glob(os.path.join(patient_dir, "*-t2f.nii.gz"))
    if not flair_files:
        raise HTTPException(status_code=404, detail="FLAIR file not found")
        
    flair_path = flair_files[0]
    flair_img = nib.load(flair_path)
    flair_data = flair_img.get_fdata().astype(np.float32)
    
    if slice_idx < 0 or slice_idx >= flair_data.shape[2]:
        raise HTTPException(status_code=400, detail="Invalid slice index")
        
    img_slice = flair_data[:, :, slice_idx]
    
    # Load mask if exists
    mask_path = f"data/processed/mask_{scan_id}.npy"
    mask_slice = None
    if os.path.exists(mask_path):
        mask_data = np.load(mask_path)
        mask_slice = mask_data[:, :, slice_idx]
        
    # Generate image
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(img_slice, cmap='gray')
    if mask_slice is not None and np.sum(mask_slice) > 0:
        ax.imshow(mask_slice, cmap='jet', alpha=0.5)
    ax.axis('off')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    from fastapi.responses import Response
    return Response(content=buf.read(), media_type="image/png")

@app.get("/scans/{scan_id}/report")
def get_scan_report(scan_id: int, db: Session = Depends(get_db)):
    report_path = f"data/processed/report_{scan_id}.pdf"
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")
        
    from fastapi.responses import FileResponse
    return FileResponse(report_path, media_type="application/pdf", filename=f"report_{scan_id}.pdf")
@app.get("/scans/{scan_id}")
def get_scan_details(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    return {
        "id": scan.id,
        "patient_id": scan.patient_id,
        "status": scan.status,
        "tumor_volume_cm3": scan.tumor_volume_cm3,
        "conclusion": scan.conclusion,
        "tumor_nature": scan.tumor_nature
    }
@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("Radiologist"))):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    db.query(Scan).filter(Scan.patient_id == patient_id).delete()
    db.delete(patient)
    db.commit()
    
    add_secure_log(f"Користувач {current_user.username} видалив пацієнта ID {patient_id}", db)
    return {"status": "success"}

@app.delete("/scans/{scan_id}")
def delete_scan(scan_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("Radiologist"))):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    db.delete(scan)
    db.commit()
    
    add_secure_log(f"Користувач {current_user.username} видалив скан ID {scan_id}", db)
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)



