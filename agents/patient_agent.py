from database.db import get_patient, get_patient_consultations
from graph.state import AssistantState


def run_patient_context(state: AssistantState) -> dict:
    patient_id = state.get("patient_id")
    if patient_id is None:
        return {
            "patient_context": {
                "available": False,
                "missing_information": ["No patient selected"],
                "recent_consultations": [],
            },
            "agent_status": state["agent_status"]
            + [{"agent": "Patient Context Agent", "status": "success", "detail": "No patient selected; no history used."}],
        }

    try:
        patient = get_patient(patient_id)
        if patient is None:
            raise ValueError("The selected patient profile was not found.")
        consultations = get_patient_consultations(patient_id, limit=3)
        context = {
            "available": True,
            "name": patient.name,
            "age": patient.age,
            "medical_history": patient.medical_history,
            "allergies": patient.allergies,
            "medications": patient.medications,
            "recent_consultations": [
                {"question": item.user_query, "response": item.assistant_response}
                for item in consultations
            ],
            "missing_information": [
                label
                for label, value in (
                    ("age", patient.age),
                    ("medical history", patient.medical_history),
                    ("allergies", patient.allergies),
                    ("medications", patient.medications),
                )
                if not value
            ],
        }
        return {
            "patient_context": context,
            "agent_status": state["agent_status"]
            + [{"agent": "Patient Context Agent", "status": "success", "detail": "Loaded only the selected patient's profile and recent consultations."}],
        }
    except Exception as exc:
        return {
            "patient_context": {"available": False, "missing_information": ["Patient data unavailable"], "recent_consultations": []},
            "agent_status": state["agent_status"]
            + [{"agent": "Patient Context Agent", "status": "failed", "detail": str(exc)}],
        }