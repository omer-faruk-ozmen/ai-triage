from datetime import datetime
import hashlib
import json
import os
from flask import request
from dotenv import load_dotenv

from models import Conclusion, Diagnosis, Examination, Intervention
from repositories.diagnosis_repository import DiagnosisRepository
from repositories.examination_repository import ExaminationRepository
from repositories.intervention_repository import InterventionRepository
from repositories.conclusion_repository import ConclusionRepository

load_dotenv()

BLACKLIST_PATH = os.getenv('BLACKLIST_PATH')
DATABASE_PATH = os.getenv('DATABASE_PATH')

conclusion_repo = ConclusionRepository(DATABASE_PATH)
diagnosis_repo = DiagnosisRepository(DATABASE_PATH)
examination_repo = ExaminationRepository(DATABASE_PATH)
intervention_repo = InterventionRepository(DATABASE_PATH)

def get_client_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

def is_ip_blacklisted(ip):
    with open(BLACKLIST_PATH, 'r') as f:
        blacklist = f.read().splitlines()
    return ip in blacklist

def is_authenticated(password):
    md5_hash = hashlib.md5(password.encode())
    hash = md5_hash.hexdigest()
    if hash == os.getenv('PASSWORD'):
        return True
    return False

def create_prompt(patient):
    prompt = 'This GPT is designed to support the triage process in the emergency department setting. Based on the information provided about the patient, it determines in which area (green, yellow, or red) the patient should be seen in the ED and gives only the triage result ("Green", "Yellow", or "Red"). It then lists in json the maximum 10 possible preliminary diagnoses for this patient, the maximum 10 tests that should be ordered, and the maximum 10 treatment recommendations that should be started, ranked from most likely to least likely. The response format is concise, including the triage result and the ranked preliminary diagnoses. GPT helps to perform fast and effective triage in the emergency department environment by carefully evaluating the patient information provided. Example return value: { "triage_class": "Triage result", "triage_code": "#HexCode (any of #FF0000, #0B6623 or #FFF200)", "pre_diag": ["Prediagnosis", "Prediagnosis", "Prediagnosis"], "examination": ["examin ", "examin ", "examin"], "treatment": ["treatment ", "treatment ", "treatment"]} '
    prompt += f" Patient information: Age: {patient.age}, Gender: {patient.gender}. Complaints: {patient.complaints}, Duration of complaint: {patient.duration}. Vital signs: Blood pressure {patient.blood_pressure} mmHg, Pulse {patient.pulse} bpm, Respiratory rate {patient.respiratory_rate} breaths/minute, Temperature {patient.temperature} °C. Saturation %{patient.saturation}. Chronic diseases: {patient.chronic_diseases}. Medications in use: {patient.medications}, Allergy history: {patient.allergy_history}, Surgical history: {patient.surgical_history}. Short summary of complaint in patient's own words: \"{patient.summary}\""
    prompt += " please give results in turkish"
    return prompt

def get_current_date():
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")


def process_patient_data(patient_id,response,prompt):

    data = json.loads(response)

    triage_class = data['triage_class']
    triage_code = data['triage_code']
    
    conclusion_repo.add(Conclusion(patient_id=patient_id,triage_class=triage_class,triage_code=triage_code,prompt=prompt))
    
    for diag in data['pre_diag']:
        diagnosis_repo.add(Diagnosis(patient_id=patient_id,diagnosis=diag))
    
    for exam in data['examination']:
        examination_repo.add(Examination(patient_id=patient_id, examination=exam))

    for treatment in data['treatment']:
        intervention_repo.add(Intervention(patient_id=patient_id, intervention=treatment))