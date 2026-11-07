import re

from langgraph.graph import END, START, StateGraph

from agents.knowledge_agent import run_medical_knowledge
from agents.patient_agent import run_patient_context
from agents.response_agent import run_medical_response
from graph.state import AssistantState

EMERGENCY_PATTERNS = (
    r"\bcan't breathe\b",
    r"\bcannot breathe\b",
    r"\bsevere trouble breathing\b",
    r"\bchoking\b",
    r"\bunconscious\b",
    r"\bnot waking\b",
    r"\bseizure\b",
    r"\bstroke symptoms?\b",
    r"\bface drooping\b",
    r"\bsudden weakness\b",
    r"\bchest pain\b",
    r"\bsevere bleeding\b",
    r"\bsuicid(?:e|al)\b",
    r"\boverdose\b",
)
EMERGENCY_MESSAGE = (
    "This may be an emergency. Contact your local emergency services now or go to the nearest emergency department. "
    "Do not wait for an online response."
)


def is_emergency(question: str) -> bool:
    normalized = question.lower()
    return any(re.search(pattern, normalized) for pattern in EMERGENCY_PATTERNS)


def build_graph():
    graph = StateGraph(AssistantState)
    graph.add_node("patient_context", run_patient_context)
    graph.add_node("medical_knowledge", run_medical_knowledge)
    graph.add_node("medical_response", run_medical_response)
    graph.add_edge(START, "patient_context")
    graph.add_edge("patient_context", "medical_knowledge")
    graph.add_edge("medical_knowledge", "medical_response")
    graph.add_edge("medical_response", END)
    return graph.compile()


_workflow = build_graph()


def run_assistant(question: str, patient_id: int | None = None, demo_mode: bool = False) -> dict:
    clean_question = question.strip()
    if not clean_question:
        raise ValueError("Enter a question before sending.")
    if is_emergency(clean_question):
        return {
            "question": clean_question,
            "answer": EMERGENCY_MESSAGE,
            "response_mode": "emergency",
            "patient_context": {},
            "retrieved_documents": [],
            "agent_status": [],
        }
    state: AssistantState = {
        "question": clean_question,
        "patient_id": patient_id,
        "demo_mode": demo_mode,
        "patient_context": {},
        "retrieved_documents": [],
        "answer": "",
        "response_mode": "unavailable",
        "agent_status": [],
    }
    return _workflow.invoke(state)