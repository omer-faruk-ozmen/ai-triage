from typing import List
from models import Conclusion
from repositories.base_repository import BaseRepository
from database import Database

class ConclusionRepository(BaseRepository[Conclusion]):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def add(self, conclusion: Conclusion):
        query = '''INSERT INTO conclusions (patient_id, triage_class, triage_code, prompt, result) 
                   VALUES (?, ?, ?, ?, ?)'''
        with Database(self.db_path) as db:
            db.execute(query, (conclusion.patient_id, conclusion.triage_class, conclusion.triage_code,
                                conclusion.prompt, conclusion.result))

    def get(self, conclusion_id: int) -> Conclusion:
        query = '''SELECT * FROM conclusions WHERE id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (conclusion_id,))
            row = db.fetchone()
            return Conclusion(*row) if row else None

    def list(self) -> List[Conclusion]:
        query = '''SELECT * FROM conclusions'''
        with Database(self.db_path) as db:
            db.execute(query)
            rows = db.fetchall()
            return [Conclusion(*row) for row in rows]

    def update(self, conclusion: Conclusion):
        query = '''UPDATE conclusions SET patient_id = ?, triage_class = ?, triage_code = ?, 
                   prompt = ?, result = ? WHERE id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (conclusion.patient_id, conclusion.triage_class, conclusion.triage_code,
                                conclusion.prompt, conclusion.result, conclusion.id))

    def delete(self, conclusion_id: int):
        query = '''DELETE FROM conclusions WHERE id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (conclusion_id,))
