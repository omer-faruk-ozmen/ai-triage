import os
from flask import Flask, render_template, request, redirect, url_for, flash, g
from repositories.patient_repository import PatientRepository
from models import Patient
import helpers
import downloads
from database import init_db,DATABASE_PATH

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

init_db()
db_path = DATABASE_PATH 
patient_repo = PatientRepository(db_path)

@app.before_request
def before_request():
    g.client_ip = helpers.get_client_ip()

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        client_ip = g.client_ip
        if helpers.is_ip_blacklisted(client_ip):
            flash('Your IP is blacklisted. You cannot add patients.', 'danger')
            return redirect(url_for('add_patient'))

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

            new_id = patient_repo.add(patient)
            return redirect(url_for('patient_detail', patient_id=new_id))
        except Exception as e:
            flash('Error occurred in insert operation: ' + str(e), 'danger')

    return render_template('form.html')

@app.route('/list')
def list_patients():
    patients = patient_repo.list()
    return render_template('list.html', rows=patients)

@app.route('/patient/<int:patient_id>', methods=['GET'])
def patient_detail(patient_id):
    patient = patient_repo.get_all_relationships(patient_id)
    if patient:
        return render_template('patient_detail.html', patient=patient)
    else:
        return render_template('404.html'), 404

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):

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

    is_auth = helpers.is_authenticated(password)
    if is_auth:
        patient_repo.delete(patient_id)
        flash('Patient deleted successfully!', 'success')
    else:
        flash('Incorrect password. Patient not deleted.', 'danger')

    return redirect(url_for('list_patients'))

@app.route('/download')
def download_excel_route():
    return downloads.download_excel()

@app.route('/download_json')
def download_json_route():
    return downloads.download_json()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
