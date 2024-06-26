import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH')

def get_db():
    return sqlite3.connect(DATABASE_PATH)

def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        print("Database connected successfully")
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER,
            gender TEXT,
            complaints TEXT,
            duration INTEGER,
            blood_pressure TEXT,
            pulse INTEGER,
            respiratory_rate INTEGER,
            temperature REAL,
            saturation INTEGER,
            chronic_diseases TEXT,
            medications TEXT,
            allergy_history TEXT,
            surgical_history TEXT,
            summary TEXT,
            date TEXT,
            ip_address TEXT
        );

        CREATE TABLE IF NOT EXISTS diagnosis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            diagnosis TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS examinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            examination TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS interventions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            intervention TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS conclusions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            triage_class TEXT,
            triage_code TEXT,
            prompt TEXT,
            result TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );
        ''')
        print("Table created successfully")



class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor

    def commit(self):
        self.conn.commit()

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def lastrowid(self):
        return self.cursor.lastrowid

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()
