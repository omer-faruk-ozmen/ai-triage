# models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Patient:
    id: int
    age: str = ''
    gender: str = ''
    complaints: str = ''
    duration: str = ''
    blood_pressure: str = ''
    pulse: str = ''
    respiratory_rate: str = ''
    temperature: str = ''
    saturation: str = ''
    chronic_diseases: str = ''
    medications: str = ''
    allergy_history: str = ''
    surgical_history: str = ''
    summary: str = ''
    date: str = ''
    ip_address: str = ''

@dataclass
class Diagnosis:
    id: int
    patient_id: int
    diagnosis: str

@dataclass
class Examination:
    id: int
    patient_id: int
    examination: str

@dataclass
class Intervention:
    id: int
    patient_id: int
    intervention: str

@dataclass
class Conclusion:
    id: int
    patient_id: int
    triage_class: str
    triage_code: str
    prompt: str
    result: str

