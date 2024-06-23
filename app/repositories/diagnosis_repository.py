from typing import List
from models import Diagnosis
from repositories.base_repository import BaseRepository
from database import Database

class DiagnosisRepository(BaseRepository[Diagnosis]):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def add(self, diagnosis: Diagnosis):
        query = '''INSERT INTO diagnosis (patient_id, diagnosis) VALUES (?, ?)'''
        with Database(self.db_path) as db:
            db.execute(query, (diagnosis.patient_id, diagnosis.diagnosis))

    def get(self, diagnosis_id: int) -> Diagnosis:
        query = '''SELECT * FROM diagnosis WHERE id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (diagnosis_id,))
            row = db.fetchone()
            return Diagnosis(*row) if row else None

    def list(self) -> List[Diagnosis]:
        query = '''SELECT * FROM diagnosis'''
        with Database(self.db_path) as db:
            db.execute(query)
            rows = db.fetchall()
            return [Diagnosis(*row) for row in rows]

    def update(self, diagnosis: Diagnosis):
        query = '''UPDATE diagnosis SET patient_id = ?, diagnosis = ? WHERE id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (diagnosis.patient_id, diagnosis.diagnosis, diagnosis.id))

    def delete(self, diagnosis_id: int):
        query = '''DELETE FROM diagnosis WHERE id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (diagnosis_id,))
