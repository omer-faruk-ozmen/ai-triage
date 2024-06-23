from datetime import datetime
import hashlib
import os
from flask import request
from dotenv import load_dotenv

load_dotenv()

BLACKLIST_PATH = os.getenv('BLACKLIST_PATH')

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

def create_prompt(age, gender, complaints, duration, bloodPressure, pulse, respiratoryRate, temperature, saturation, chronicDiseases, medications, allergyHistory, surgicalHistory, summary):
    prompt = 'This GPT is designed to support the triage process in the emergency department setting. Based on the information provided about the patient, it determines in which area (green, yellow, or red) the patient should be seen in the ED and gives only the triage result ("Green", "Yellow", or "Red"). It then lists in json the maximum 10 possible preliminary diagnoses for this patient, the maximum 10 tests that should be ordered, and the maximum 10 treatment recommendations that should be started, ranked from most likely to least likely. The response format is concise, including the triage result and the ranked preliminary diagnoses. GPT helps to perform fast and effective triage in the emergency department environment by carefully evaluating the patient information provided. Example return value: { "triage": "Triage result", "triageColorCode": "#HexCode (any of #FF0000, #0B6623 or #FFF200)", "preDiag": ["1 : Prediagnosis", "2 : Prediagnosis", "3 : Prediagnosis"], "examination": ["1 : examin ", "2 : examin ", "3 : examin"], "treatment": ["1 : treatment ", "2 : treatment ", "3 : treatment"]} '
    prompt += f" Patient information: Age: {age}, Gender: {gender}. Complaints: {complaints}, Duration of complaint: {duration}. Vital signs: Blood pressure {bloodPressure} mmHg, Pulse {pulse} bpm, Respiratory rate {respiratoryRate} breaths/minute, Temperature {temperature} °C. Saturation %{saturation}. Chronic diseases: {chronicDiseases}. Medications in use: {medications}, Allergy history: {allergyHistory}, Surgical history: {surgicalHistory}. Short summary of complaint in patient's own words: \"{summary}\""
    prompt += " please give results in turkish"
    return prompt

def get_current_date():
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")
