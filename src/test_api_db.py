import os
import sys
import base64
import requests

def interactive_test():
    url = "http://localhost:8001"
    
    print("=== NeuroSegment AI: Тестування з Безпекою ===")
    
    # Симуляція логіну для отримання ролі
    print("Введіть дані для авторизації:")
    username = input("Username (наприклад, doctor або admin): ").strip()
    
    headers = {
        "username": username
    }
    
    print("\nОберіть дію:")
    print("1. Створити нового пацієнта")
    print("2. Обрати існуючого пацієнта")
    
    choice = input("Ваш вибір (1 або 2): ").strip()
    
    patient_id = None
    
    if choice == "1":
        print("\n--- Створення нового пацієнта ---")
        first_name = input("Ім'я: ").strip()
        last_name = input("Прізвище: ").strip()
        dob = input("Дата народження (YYYY-MM-DD): ").strip()
        phone = input("Номер телефону: ").strip()
        notes = input("Нотатки (необов'язково): ").strip()
        
        # Створення пацієнта через API
        try:
            response = requests.post(f"{url}/patients", params={
                "first_name": first_name,
                "last_name": last_name,
                "dob": dob,
                "phone": phone,
                "notes": notes
            }, headers=headers)
            
            if response.status_code == 200:
                patient = response.json()
                patient_id = patient['id']
                print(f"Успішно створено пацієнта! ID: {patient_id}")
            elif response.status_code == 403:
                print("Помилка: Недостатньо прав доступу для створення пацієнта.")
                return
            elif response.status_code == 401:
                print("Помилка авторизації. Невірний username.")
                return
            else:
                print(f"Помилка створення пацієнта: {response.status_code}")
                print(response.text)
                return
        except requests.exceptions.ConnectionError:
            print("Помилка підключення до сервера. Переконайтеся, що сервер запущено на порту 8001.")
            return
            
    elif choice == "2":
        print("\n--- Вибір існуючого пацієнта ---")
        try:
            response = requests.get(f"{url}/patients", headers=headers)
            if response.status_code == 200:
                patients = response.json()
                if not patients:
                    print("Пацієнтів у базі немає. Створіть нового.")
                    return
                    
                print("\nСписок пацієнтів (Дані розшифровані сервером):")
                for p in patients:
                    print(f"ID: {p['id']} | {p['first_name']} {p['last_name']} | ДН: {p['dob']}")
                    
                p_id_input = input("\nВведіть ID обраного пацієнта: ").strip()
                try:
                    patient_id = int(p_id_input)
                except ValueError:
                    print("Некоректний ID.")
                    return
            elif response.status_code == 403:
                print("Помилка: Недостатньо прав доступу для перегляду пацієнтів.")
                return
            else:
                print(f"Помилка отримання списку пацієнтів: {response.status_code}")
                return
        except requests.exceptions.ConnectionError:
            print("Помилка підключення до сервера.")
            return
    else:
        print("Невірний вибір.")
        return
        
    print("\n--- Параметри аналізу ---")
    scan_number = input("Введіть номер знімків nnnnn (наприклад, 00005): ").strip()
    
    print(f"\nВідправка запиту на аналіз для пацієнта ID {patient_id}, знімки {scan_number}...")
    print("(Перед аналізом ШІ застосовується Spatial Smoothing для захисту від атак)")
    
    try:
        response = requests.post(f"{url}/analyze", params={
            "patient_id": patient_id,
            "scan_number": scan_number
        }, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("\n=== Успішно отримано відповідь! ===")
            patient_data = data['patient']
            scan_data = patient_data['scans'][0]
            
            print(f"Пацієнт: {patient_data['first_name']} {patient_data['last_name']}")
            print(f"Об'єм пухлини: {scan_data['tumor_volume_cm3']:.2f} см³")
            print(f"Висновок: {scan_data['conclusion']}")
            
            pdf_base64 = data['pdf_report_base64']
            pdf_bytes = base64.b64decode(pdf_base64)
            
            output_pdf = f"report_patient_{patient_id}_{scan_number}_secure.pdf"
            with open(output_pdf, "wb") as f:
                f.write(pdf_bytes)
            print(f"\nЗвіт (захищений) збережено у: {output_pdf}")
            print("Дії залогівано в захищений журнал (Hash Chains)")
            
        else:
            print(f"\nПомилка сервера: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("Помилка підключення до сервера.")

if __name__ == "__main__":
    interactive_test()
