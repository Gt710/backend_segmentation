import os
import sys
import argparse
import base64
import requests

def test_predict(t1_path, t1c_path, t2_path, flair_path, output_pdf="report.pdf"):
    url = "http://localhost:8001/predict"
    
    print(f"Відправка запиту на {url}...")
    
    # Перевірка наявності файлів
    for p in [t1_path, t1c_path, t2_path, flair_path]:
        if not os.path.exists(p):
            print(f"Помилка: Файл не знайдено: {p}")
            return
            
    files = {
        't1': open(t1_path, 'rb'),
        't1c': open(t1c_path, 'rb'),
        't2': open(t2_path, 'rb'),
        'flair': open(flair_path, 'rb')
    }
    
    try:
        response = requests.post(url, files=files)
        
        # Закриваємо файли
        for f in files.values():
            f.close()
            
        if response.status_code == 200:
            data = response.json()
            print("Успішно отримано відповідь!")
            print(f"Об'єм пухлини: {data['volume_cm3']:.2f} см³")
            print(f"Висновок: {data['conclusion']}")
            
            pdf_base64 = data['pdf_report_base64']
            pdf_bytes = base64.b64decode(pdf_base64)
            
            with open(output_pdf, "wb") as f:
                f.write(pdf_bytes)
            print(f"Звіт збережено у: {output_pdf}")
            
        else:
            print(f"Помилка сервера: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("Помилка підключення. Переконайтеся, що сервер API запущено (uvicorn src.api:app --reload)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Тестування API сегментації пухлин мозку")
    parser.add_argument("--t1", type=str, help="Шлях до файлу T1")
    parser.add_argument("--t1c", type=str, help="Шлях до файлу T1c")
    parser.add_argument("--t2", type=str, help="Шлях до файлу T2")
    parser.add_argument("--flair", type=str, help="Шлях до файлу FLAIR")
    parser.add_argument("--output", type=str, default="report.pdf", help="Назва вихідного PDF файлу")
    
    args = parser.parse_args()
    
    # Значення за замовчуванням (використовуємо знайденого пацієнта)
    default_patient_dir = "data/raw/BraTS-GLI/train/BraTS-GLI-00006-100"
    
    t1 = args.t1 or os.path.join(default_patient_dir, "BraTS-GLI-00006-100-t1n.nii.gz")
    t1c = args.t1c or os.path.join(default_patient_dir, "BraTS-GLI-00006-100-t1c.nii.gz")
    t2 = args.t2 or os.path.join(default_patient_dir, "BraTS-GLI-00006-100-t2w.nii.gz")
    flair = args.flair or os.path.join(default_patient_dir, "BraTS-GLI-00006-100-t2f.nii.gz")
    
    test_predict(t1, t1c, t2, flair, args.output)
