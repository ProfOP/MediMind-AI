from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from config import DB_PATH
from database.models import Base, Consultation, Patient


@lru_cache(maxsize=8)
def _engine_for(path: str) -> object:
    database_path = Path(path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )


@contextmanager
def _session(db_path: str | Path = DB_PATH) -> Iterator[Session]:
    factory = sessionmaker(bind=_engine_for(str(Path(db_path))), expire_on_commit=False)
    session = factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(db_path: str | Path = DB_PATH) -> None:
    Base.metadata.create_all(_engine_for(str(Path(db_path))))


def list_patients(db_path: str | Path = DB_PATH) -> list[Patient]:
    with _session(db_path) as session:
        return list(session.scalars(select(Patient).order_by(Patient.name)))


def get_patient(patient_id: int, db_path: str | Path = DB_PATH) -> Patient | None:
    with _session(db_path) as session:
        return session.get(Patient, patient_id)


def create_patient(
    name: str,
    age: int | None = None,
    medical_history: str = "",
    allergies: str = "",
    medications: str = "",
    db_path: str | Path = DB_PATH,
) -> Patient:
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("Enter a patient name.")
    if age is not None and not 0 <= age <= 125:
        raise ValueError("Age must be between 0 and 125.")
    patient = Patient(
        name=clean_name,
        age=age,
        medical_history=medical_history.strip(),
        allergies=allergies.strip(),
        medications=medications.strip(),
    )
    with _session(db_path) as session:
        session.add(patient)
        session.commit()
        session.refresh(patient)
        return patient


def update_patient(
    patient_id: int,
    name: str,
    age: int | None,
    medical_history: str,
    allergies: str,
    medications: str,
    db_path: str | Path = DB_PATH,
) -> Patient:
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("Enter a patient name.")
    if age is not None and not 0 <= age <= 125:
        raise ValueError("Age must be between 0 and 125.")
    with _session(db_path) as session:
        patient = session.get(Patient, patient_id)
        if patient is None:
            raise ValueError("Patient profile not found.")
        patient.name = clean_name
        patient.age = age
        patient.medical_history = medical_history.strip()
        patient.allergies = allergies.strip()
        patient.medications = medications.strip()
        session.commit()
        session.refresh(patient)
        return patient


def save_consultation(
    patient_id: int,
    user_query: str,
    assistant_response: str,
    db_path: str | Path = DB_PATH,
) -> Consultation:
    if not user_query.strip() or not assistant_response.strip():
        raise ValueError("A consultation needs both a question and a response.")
    with _session(db_path) as session:
        if session.get(Patient, patient_id) is None:
            raise ValueError("Patient profile not found.")
        consultation = Consultation(
            patient_id=patient_id,
            user_query=user_query.strip(),
            assistant_response=assistant_response.strip(),
        )
        session.add(consultation)
        session.commit()
        session.refresh(consultation)
        return consultation


def get_patient_consultations(
    patient_id: int,
    limit: int = 20,
    db_path: str | Path = DB_PATH,
) -> list[Consultation]:
    with _session(db_path) as session:
        statement = (
            select(Consultation)
            .where(Consultation.patient_id == patient_id)
            .order_by(Consultation.created_at.desc(), Consultation.id.desc())
            .limit(max(1, min(limit, 100)))
        )
        return list(session.scalars(statement))