from typing import List
from models import Examination
from repositories.base_repository import BaseRepository
from database import Database

class ExaminationRepository(BaseRepository[Examination]):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def add(self, examination: Examination):
        query = '''INSERT INTO examinations (patient_id, examination) VALUES (?, ?)'''
        with Database(self.db_path) as db:
            db.execute(query, (examination.patient_id, examination.examination))

    def get(self, examination_id: int) -> Examination:
        query = '''SELECT * FROM examinations WHERE id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (examination_id,))
            row = db.fetchone()
            return Examination(*row) if row else None

    def list(self) -> List[Examination]:
        query = '''SELECT * FROM examinations'''
        with Database(self.db_path) as db:
            db.execute(query)
            rows = db.fetchall()
            return [Examination(*row) for row in rows]

    def update(self, examination: Examination):
        query = '''UPDATE examinations SET patient_id = ?, examination = ? WHERE id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (examination.patient_id, examination.examination, examination.id))

    def delete(self, examination_id: int):
        query = '''DELETE FROM examinations WHERE id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (examination_id,))
