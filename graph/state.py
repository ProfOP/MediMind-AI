from typing import TypedDict


class AgentStatus(TypedDict):
    agent: str
    status: str
    detail: str


class AssistantState(TypedDict):
    question: str
    patient_id: int | None
    demo_mode: bool
    patient_context: dict
    retrieved_documents: list[dict]
    answer: str
    response_mode: str
    agent_status: list[AgentStatus]