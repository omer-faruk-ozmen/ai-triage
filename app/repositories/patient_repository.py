from typing import List

import pandas as pd
from models import Conclusion, Diagnosis, Examination, Intervention, Patient
from repositories.base_repository import BaseRepository
from database import Database

class PatientRepository(BaseRepository[Patient]):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def add(self, patient: Patient):
        query = '''INSERT INTO patients (age, gender, complaints, duration, blood_pressure, pulse, respiratory_rate, temperature, saturation, chronic_diseases, medications, allergy_history, surgical_history, summary, date, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        with Database(self.db_path) as db:
            db.execute(query, (patient.age, patient.gender, patient.complaints, patient.duration, patient.blood_pressure, patient.pulse, patient.respiratory_rate, patient.temperature, patient.saturation, patient.chronic_diseases, patient.medications, patient.allergy_history, patient.surgical_history, patient.summary, patient.date, patient.ip_address))
            
        return db.lastrowid()

    def get(self, patient_id: int) -> Patient:
        query = '''SELECT * FROM patients WHERE id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (patient_id,))
            row = db.fetchone()
            return Patient(*row) if row else None

    def list(self) -> List[Patient]:
        query = '''SELECT * FROM patients'''
        with Database(self.db_path) as db:
            db.execute(query)
            rows = db.fetchall()
            return [Patient(*row) for row in rows]
        
    def list_paginated(self, start: int, per_page: int):
        query = '''SELECT * FROM patients LIMIT ? OFFSET ?'''
        with Database(self.db_path) as db:
            db.execute(query, (per_page, start))
            rows = db.fetchall()
            return [Patient(*row) for row in rows]
        
    def count(self):
        query = '''SELECT COUNT(*) FROM patients'''
        with Database(self.db_path) as db:
            db.execute(query)
            count = db.fetchone()[0]
            return count

    def update(self, patient: Patient):
        query = '''UPDATE patients SET age = ?, gender = ?, complaints = ?, duration = ?, blood_pressure = ?, pulse = ?, respiratory_rate = ?, temperature = ?, saturation = ?, chronic_diseases = ?, medications = ?, allergy_history = ?, surgical_history = ?, summary = ?, date = ?, ip_address = ? WHERE id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (patient.age, patient.gender, patient.complaints, patient.duration, patient.blood_pressure, patient.pulse, patient.respiratory_rate, patient.temperature, patient.saturation, patient.chronic_diseases, patient.medications, patient.allergy_history, patient.surgical_history, patient.summary, patient.date, patient.ip_address, patient.id))

    def delete(self, patient_id: int):
        query = '''DELETE FROM patients WHERE id = ?'''
        
        with Database(self.db_path) as db:
            db.execute(query, (patient_id,))

    def get_conclusion_by_patient_id(self, patient_id: int) -> Conclusion:
        query = '''SELECT * FROM conclusions WHERE patient_id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (patient_id,))
            row = db.fetchone()
            return Conclusion(*row) if row else None
        

    def get_all_relationships(self, patient_id: int) -> Patient:
        patient = self.get(patient_id)
        if not patient:
            return None

        # Diğer ilişkili verileri al
        diagnosis = self._get_diagnosis(patient_id)
        examinations = self._get_examinations(patient_id)
        interventions = self._get_interventions(patient_id)
        conclusion = self._get_conclusion(patient_id)

        # Patient nesnesini güncelle
        patient.diagnosis = diagnosis
        patient.examinations = examinations
        patient.interventions = interventions
        patient.conclusion = conclusion

        return patient
    
    def get_all_patients_with_relationships(self) -> pd.DataFrame:
        query = '''SELECT * FROM patients'''
        with Database(self.db_path) as db:
            db.execute(query)
            patients = db.fetchall()

        data = []
        for patient in patients:
            patient_data = list(patient)
            diagnosis = self._get_diagnosis(patient[0])
            examinations = self._get_examinations(patient[0])
            interventions = self._get_interventions(patient[0])
            conclusion = self._get_conclusion(patient[0])

            # Adding diagnosis, examinations, interventions, and conclusion to patient_data
            patient_data.extend([diagnosis, examinations, interventions, conclusion])
            data.append(patient_data)

        columns = [
            'id', 'age', 'gender', 'complaints', 'duration', 'blood_pressure', 'pulse',
            'respiratory_rate', 'temperature', 'saturation', 'chronic_diseases', 'medications',
            'allergy_history', 'surgical_history', 'summary', 'date', 'ip_address',
            'diagnosis', 'examinations', 'interventions', 'conclusion'
        ]

        df = pd.DataFrame(data, columns=columns)
        return df

    def _get_diagnosis(self, patient_id: int) -> List[Diagnosis]:
        query = '''SELECT * FROM diagnosis WHERE patient_id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (patient_id,))
            rows = db.fetchall()
            return [Diagnosis(*row) for row in rows]

    def _get_examinations(self, patient_id: int) -> List[Examination]:
        query = '''SELECT * FROM examinations WHERE patient_id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (patient_id,))
            rows = db.fetchall()
            return [Examination(*row) for row in rows]

    def _get_interventions(self, patient_id: int) -> List[Intervention]:
        query = '''SELECT * FROM interventions WHERE patient_id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (patient_id,))
            rows = db.fetchall()
            return [Intervention(*row) for row in rows]

    def _get_conclusion(self, patient_id: int) -> Conclusion:
        query = '''SELECT * FROM conclusions WHERE patient_id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (patient_id,))
            row = db.fetchone()
            return Conclusion(*row) if row else None