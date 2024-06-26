import pandas as pd
from io import BytesIO
from flask import send_file, jsonify, make_response
from repositories.patient_repository import PatientRepository
import database

db_path = database.DATABASE_PATH 
patient_repo = PatientRepository(db_path)

def download_excel():
    with database.Database(db_path) as db:
        patients_df = patient_repo.get_all_patients_with_relationships()

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    patients_df.to_excel(writer, index=False, sheet_name='patients')
    writer.close()
    output.seek(0)

    return send_file(output, as_attachment=True, download_name='patients.xlsx')

def download_json():
    db = database.get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM patients")
    rows = cursor.fetchall()
    db.close()
    
    # Task 
    patients = [{'name': row[0], 'email': row[1], 'message': row[2]} for row in rows]
    response = make_response(jsonify(patients))
    response.headers['Content-Disposition'] = 'attachment; filename=patients.json'
    response.mimetype = 'application/json'
    return response
