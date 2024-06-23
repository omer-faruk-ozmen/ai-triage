from typing import List
from models import Intervention
from repositories.base_repository import BaseRepository
from database import Database

class InterventionRepository(BaseRepository[Intervention]):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def add(self, intervention: Intervention):
        query = '''INSERT INTO interventions (patient_id, intervention) VALUES (?, ?)'''
        with Database(self.db_path) as db:
            db.execute(query, (intervention.patient_id, intervention.intervention))

    def get(self, intervention_id: int) -> Intervention:
        query = '''SELECT * FROM interventions WHERE id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (intervention_id,))
            row = db.fetchone()
            return Intervention(*row) if row else None

    def list(self) -> List[Intervention]:
        query = '''SELECT * FROM interventions'''
        with Database(self.db_path) as db:
            db.execute(query)
            rows = db.fetchall()
            return [Intervention(*row) for row in rows]

    def update(self, intervention: Intervention):
        query = '''UPDATE interventions SET patient_id = ?, intervention = ? WHERE id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (intervention.patient_id, intervention.intervention, intervention.id))

    def delete(self, intervention_id: int):
        query = '''DELETE FROM interventions WHERE id = ?'''
        with Database(self.db_path) as db:
            db.execute(query, (intervention_id,))
