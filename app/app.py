from datetime import datetime
from math import ceil
import os
from flask import Flask, render_template, request, redirect, session, url_for, flash, g
from backup import backup_database, delete_old_backup
from repositories.conclusion_repository import ConclusionRepository
from repositories.patient_repository import PatientRepository
from models import Conclusion, Patient
import helpers
import downloads
import requests_handler
from database import init_db,DATABASE_PATH

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

init_db()
db_path = DATABASE_PATH 
patient_repo = PatientRepository(db_path)
conclusion_repo = ConclusionRepository(db_path)

@app.before_request
def before_request():
    g.client_ip = helpers.get_client_ip()

@app.route('/')
def home():
    return render_template('home.html')

@app.before_request
def before_request():
    g.client_ip = helpers.get_client_ip()
    if helpers.is_ip_blacklisted(g.client_ip):
        if request.endpoint in ['admin_page', 'admin_dashboard', 'block_ip', 'unblock_ip']:
            return render_template('404.html'), 404

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    if request.method == 'POST':
        ip_address = helpers.get_client_ip()
        password = request.form.get('password')

        # Bruteforce korumasını işle
        is_blocked = helpers.handle_bruteforce_protection(ip_address, helpers.is_admin_authenticated(password),'admin')

        if is_blocked:
            flash(f"Admin girişi için IP adresiniz {helpers.BLOCK_TIME_MINUTES} dakika boyunca engellendi.", 'danger')
            return redirect(url_for('home'))

        if helpers.is_admin_authenticated(password):
            session['admin_authenticated'] = True  # Başarıyla giriş yapan kullanıcı için session oluştur
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Yanlış şifre', 'danger')
            return redirect(url_for('admin_page'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_authenticated'):
        flash('Bu sayfaya erişim izniniz yok', 'danger')
        return redirect(url_for('admin_page'))
    
    # Blacklist dosyasını oku
    with open('data/blacklist.txt', 'r') as file:
        blacklisted_ips = file.read().splitlines()
    
    bruteforce_entries = helpers.parse_bruteforce_log(helpers.BRUTEFORCE_PATH)

    # Hastaları veritabanından çek
    patients = patient_repo.list()  # Hastaları listeleme kodu

    # Blacklist durumlarını kontrol ederek işaretlemeleri yapın
    for patient in patients:
        patient.is_blocked = helpers.is_ip_blacklisted(patient.ip_address)

    return render_template('admin_dashboard.html', blacklisted_ips=blacklisted_ips, patients=patients,bruteforce_entries=bruteforce_entries,current_ip=helpers.get_client_ip())


@app.route('/admin/block_ip', methods=['POST'])
def block_ip():
    if not session.get('admin_authenticated'):
        flash('Bu işlemi yapmaya yetkiniz yok', 'danger')
        return redirect(url_for('admin_page'))

    ip_address = request.form.get('ip_address')
    if ip_address and not helpers.is_ip_blacklisted(ip_address):  # IP zaten engellenmişse tekrar eklenmez
        with open('data/blacklist.txt', 'a') as file:
            file.write(f"{ip_address}\n")
        flash(f'IP adresi {ip_address} engellendi.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/unblock_ip', methods=['POST'])
def unblock_ip():
    if not session.get('admin_authenticated'):
        flash('Bu işlemi yapmaya yetkiniz yok', 'danger')
        return redirect(url_for('admin_page'))

    ip_address = request.form.get('ip_address')
    if ip_address and helpers.is_ip_blacklisted(ip_address):  # IP zaten engelli değilse tekrar kaldırılmaz
        with open('data/blacklist.txt', 'r') as file:
            lines = file.readlines()
        with open('data/blacklist.txt', 'w') as file:
            for line in lines:
                if line.strip() != ip_address:
                    file.write(line)
        flash(f'IP adresi {ip_address} engeli kaldırıldı.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/add', methods=['GET', 'POST'])
def add_patient():
    client_ip = g.client_ip
    if helpers.is_ip_blacklisted(client_ip):
        flash('Your IP is blacklisted. You cannot add patients.', 'danger')
        return redirect(url_for('list_patients'))
    if request.method == 'POST':
        try:
            patient = Patient(
                id=None,
                age=request.form['age'],
                gender=request.form['gender'],
                complaints=request.form['complaints'],
                duration=request.form['duration'],
                blood_pressure=request.form['bloodPressure'],
                pulse=request.form['pulse'],
                respiratory_rate=request.form['respiratoryRate'],
                temperature=request.form['temperature'],
                saturation=request.form['saturation'],
                chronic_diseases=request.form['chronicDiseases'],
                medications=request.form['medications'],
                allergy_history=request.form['allergyHistory'],
                surgical_history=request.form['surgicalHistory'],
                summary=request.form['summary'],
                date=helpers.get_current_date(),
                ip_address=client_ip
            )
            prompt = helpers.create_prompt(patient)
            response = requests_handler.generate_algorithms_with_ai(prompt)
            new_id = patient_repo.add(patient)
            helpers.process_patient_data(new_id,response,prompt)
            return redirect(url_for('patient_detail', patient_id=new_id))
        except Exception as e:
            flash('Error occurred in insert operation: ' + str(e), 'danger')
    return render_template('form.html')

@app.route('/list')
def list_patients():
    page = request.args.get('page', 1, type=int)
    per_page =request.args.get('per_page', 10, type=int)  # Sayfa başına gösterilecek veri sayısı
    total_patients = patient_repo.count()  # Toplam hasta sayısı
    total_pages = ceil(total_patients / per_page)  # Toplam sayfa sayısı

    if page > total_pages:
        page = total_pages

    start = (page - 1) * per_page
    patients = patient_repo.list_paginated(start, per_page)
    patients_with_conclusions = []

    for patient in patients:
        conclusion = patient_repo.get_conclusion_by_patient_id(patient.id)
        patient.conclusion = conclusion
        print(type(patient.date))
        patient.date = datetime.strptime(patient.date, '%d-%m-%Y %H:%M:%S')
        patient.date = datetime.strftime(patient.date, '%d-%m-%y %H:%M')
        patients_with_conclusions.append(patient)

    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_patients,
        'pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_num': page - 1,
        'next_num': page + 1,
        'iter_pages': list(range(1, total_pages + 1)) 
    }

    return render_template('list.html', rows=patients_with_conclusions, pagination=pagination,total_pages=total_pages)


@app.route('/patient/<int:patient_id>', methods=['GET'])
def patient_detail(patient_id):
    patient = patient_repo.get_all_relationships(patient_id)
    if patient:
        return render_template('patient_detail.html', patient=patient)
    else:
        return render_template('404.html'), 404

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    client_ip = g.client_ip
    if helpers.is_ip_blacklisted(client_ip):
        flash('Your IP is blacklisted. You cannot edit patients.', 'danger')
        return redirect(url_for('list_patients'))

    if request.method == 'POST':
        patient = Patient(
            id=id,
            age=request.form['age'],
            gender=request.form['gender'],
            complaints=request.form['complaints'],
            duration=request.form['duration'],
            blood_pressure=request.form['bloodPressure'],
            pulse=request.form['pulse'],
            respiratory_rate=request.form['respiratoryRate'],
            temperature=request.form['temperature'],
            saturation=request.form['saturation'],
            chronic_diseases=request.form['chronicDiseases'],
            medications=request.form['medications'],
            allergy_history=request.form['allergyHistory'],
            surgical_history=request.form['surgicalHistory'],
            summary=request.form['summary'],
            date=helpers.get_current_date(),
            ip_address=g.client_ip,
        )
        patient_repo.update(patient)
        return redirect(url_for('list_patients'))
    else:
        patient = patient_repo.get(id)
        return render_template('edit.html', patient=patient)

@app.route('/delete', methods=['POST'])
def delete_patient():
    patient_id = request.form['id']
    password = request.form['password']
    ip_address = helpers.get_client_ip()  # İstemcinin IP adresini al

    # Bruteforce korumasını işle
    is_blocked = helpers.handle_bruteforce_protection(ip_address, helpers.is_authenticated(password),'delete')

    if is_blocked:
        flash(f"Hasta silme işlemi için IP adresiniz {helpers.BLOCK_TIME_MINUTES} dakika boyunca engellendi.", 'danger')
        return redirect(url_for('home'))

    # Kullanıcı doğrulamasını helpers.py içindeki bir fonksiyonla yap
    is_auth = helpers.is_authenticated(password)

    if is_auth:
        patient_repo.delete(patient_id)
        flash('Patient deleted successfully!', 'success')
    else:
        flash('Incorrect password. Patient not deleted.', 'danger')

    return redirect(url_for('list_patients'))

@app.route('/edit-result/<int:id>', methods=['POST'])
def edit_result(id):
    result = request.form.get('result')

    conclusion = conclusion_repo.get_conclusion_by_patient_id(id)
    if conclusion:
        # Update the result
        conclusion.result = result
        conclusion_repo.update(conclusion)
        flash('Sonuç başarıyla güncellendi', 'success')
    else:
        # If no conclusion exists, create a new one
        new_conclusion = Conclusion(patient_id=id, result=result)
        conclusion_repo.add(new_conclusion)
        flash('Sonuç başarıyla eklendi', 'success')

    return redirect(url_for('list_patients'))

@app.route('/download')
def download_excel_route():
    return downloads.download_excel()

@app.route('/download_json')
def download_json_route():
    return downloads.download_json()

@app.route('/backup', methods=['POST'])
def backup():
    backup_database()
    delete_old_backup()
    return 'Yedekleme işlemi başarıyla tamamlandı'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True,port=8080)
