from graph.state import AssistantState
from rag.retriever import retrieve


def run_medical_knowledge(state: AssistantState) -> dict:
    try:
        documents = retrieve(state["question"], top_k=3)
        detail = f"Retrieved {len(documents)} local knowledge chunks." if documents else "No matching local references were found."
        return {
            "retrieved_documents": documents,
            "agent_status": state["agent_status"]
            + [{"agent": "Medical Knowledge Agent", "status": "success", "detail": detail}],
        }
    except Exception as exc:
        return {
            "retrieved_documents": [],
            "agent_status": state["agent_status"]
            + [{"agent": "Medical Knowledge Agent", "status": "failed", "detail": str(exc)}],
        }