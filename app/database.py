import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH')

def get_db():
    return sqlite3.connect(DATABASE_PATH)

def seed_data():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.executescript('''
        INSERT INTO patients (age, gender, complaints, duration, blood_pressure, pulse, respiratory_rate, temperature, saturation, chronic_diseases, medications, allergy_history, surgical_history, summary, date, ip_address)
        VALUES 
            (35, 'Male', 'Headache and fatigue', 7, '120/80', 70, 16, 37.2, 98, 'Hypertension', 'None', 'None', 'None', 'Patient presented with headache and fatigue. No other symptoms reported.', '2024-06-23', '192.168.1.1'),
            (45, 'Female', 'Chest pain and shortness of breath', 2, '140/90', 80, 18, 36.8, 99, 'None', 'Aspirin', 'None', 'None', 'Patient presented with chest pain and shortness of breath. ECG showed abnormal rhythm.', '2024-06-23', '192.168.1.2'),
            (60, 'Male', 'Abdominal pain and nausea', 5, '130/85', 75, 14, 37.0, 97, 'GERD', 'Antacids', 'None', 'Appendectomy 20 years ago', 'Patient presented with abdominal pain and nausea. History of GERD.', '2024-06-23', '192.168.1.3');

        INSERT INTO diagnosis (patient_id, diagnosis)
        VALUES
            (1, 'Migraine'),
            (1, 'Fatigue'),
            (2, 'Acute coronary syndrome'),
            (2, 'Arrhythmia'),
            (3, 'Gastritis');


        INSERT INTO examinations (patient_id, examination)
        VALUES
            (1, 'MRI of head'),
            (1, 'Blood test'),
            (2, 'ECG'),
            (2, 'Echocardiogram'),
            (3, 'Abdominal ultrasound');


        INSERT INTO interventions (patient_id, intervention)
        VALUES
            (1, 'Prescribed painkillers'),
            (2, 'Administered aspirin'),
            (2, 'Monitored in CCU'),
            (3, 'Prescribed antacids'),
            (3, 'Recommended dietary changes');

        INSERT INTO conclusions (patient_id, triage_class, triage_code, prompt, result)
        VALUES
            (1, 'Green', '#00FF00', 'Patient advised to rest and stay hydrated.', 'Patients symptoms improved with medication.'),
            (2, 'Red', '#FF0000', 'Patient transferred to CCU for monitoring.', 'Patient stabilized after intervention.'),
            (3, 'Yellow', '#FFFF00', 'Patient scheduled for follow-up examination.', 'Patient advised on dietary changes.');
        ''')

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

        if os.getenv('FLASK_ENV') =='development':
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM patients")
            count = cursor.fetchone()[0]

            if count == 0:
                seed_data()
                print("Inserted Seed Data")



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
