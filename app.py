import streamlit as st

from config import DISCLAIMER, OLLAMA_MODEL
from database.db import (
    create_patient,
    get_patient_consultations,
    init_db,
    list_patients,
    update_patient,
)
from graph.workflow import run_assistant
from rag.ingest import load_documents
from rag.retriever import get_collection, retrieve


st.set_page_config(
    page_title="MediMind AI",
    page_icon="✚",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(
    """
    <style>
    :root {
        --ink: #203b36;
        --muted: #60736e;
        --teal: #167c72;
        --line: #dce7e2;
        --surface: #ffffff;
    }
    .stApp {
        color: var(--ink);
        background: radial-gradient(ellipse at 85% 0%, #eaf4ef 0, transparent 38%), #f5f8f6;
        font-family: "Avenir Next", "Helvetica Neue", sans-serif;
    }
    section.main > div.block-container {
        max-width: 1060px;
        padding-top: 1.6rem;
        padding-bottom: 5rem;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: #edf4f0;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] * { color: var(--ink); }
    h1, h2, h3 { color: var(--ink); font-family: "Avenir Next", "Helvetica Neue", sans-serif; }
    h1 { font-size: 2rem; font-weight: 700; }
    h2 { font-size: 1.45rem; }
    h3 { font-size: 1.1rem; }
    p, label, [data-testid="stMarkdownContainer"] { color: var(--ink); }
    .mm-kicker {
        color: var(--teal);
        font-size: .72rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .mm-note { color: var(--muted); font-size: .9rem; }
    .mm-disclaimer {
        border-left: 3px solid #c65e47;
        background: #fff8f4;
        color: #563a32;
        padding: .65rem .85rem;
        border-radius: 4px;
        font-size: .9rem;
    }
    .mm-sidebar-heading {
        color: var(--muted);
        font-size: .72rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    div[data-testid="stChatMessage"] {
        color: var(--ink);
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: .9rem 1rem;
    }
    div[data-testid="stChatMessage"] p { color: var(--ink); }
    div[data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 6px;
        background: rgba(255, 255, 255, .72);
    }
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] [role="radiogroup"] { gap: .35rem; }
    div[data-testid="stRadio"] label {
        background: #eaf1ed;
        border: 1px solid transparent;
        border-radius: 5px;
        padding: .25rem .7rem;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background: #ffffff;
        border-color: #b9d1c8;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background: var(--teal);
        border-color: var(--teal);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    init_db()
except Exception as exc:
    st.error(f"Could not initialize the project-local database: {exc}")
    st.stop()

st.markdown('<div class="mm-kicker">Local educational prototype</div>', unsafe_allow_html=True)
st.title("MediMind AI")
st.markdown(f'<div class="mm-disclaimer">{DISCLAIMER}</div>', unsafe_allow_html=True)

patients = list_patients()
patient_by_label = {f"{patient.name} · #{patient.id}": patient for patient in patients}
with st.expander("Session settings", expanded=False):
    selected_label = st.selectbox("Patient", ["No patient"] + list(patient_by_label))
    selected_patient = patient_by_label.get(selected_label)
    demo_mode = st.toggle("Use labelled demo mode", value=False)
    save_history = st.checkbox("Confirm saving this chat to patient history", value=False)
    st.caption(f"Local model · {OLLAMA_MODEL}")
    st.caption("No cloud AI service is used.")

page = st.radio(
    "Workspace",
    ["Medical assistant", "Patient profile", "Knowledge base"],
    horizontal=True,
    label_visibility="collapsed",
)
st.divider()


def render_sources(sources: list[dict]) -> None:
    if not sources:
        st.caption("No local references were retrieved.")
        return
    for source in sources:
        url = source.get("source_url", "")
        title = source.get("title", "Reference")
        name = source.get("source_name", "Local knowledge base")
        if url:
            st.markdown(f"- [{title}]({url}) · {name}")
        else:
            st.markdown(f"- {title} · {name}")


if page == "Medical assistant":
    st.subheader("Medical assistant")
    st.markdown('<div class="mm-note">General information only. Patient memory is limited to the selected profile.</div>', unsafe_allow_html=True)
    patient_id = selected_patient.id if selected_patient else None
    if selected_patient:
        st.caption(f"Using profile: {selected_patient.name}")
    elif patients:
        st.caption("Choose a patient in the sidebar to include saved context, or continue without it.")
    else:
        st.caption("You can ask without a profile, or create one under Patient profile.")

    active_key = patient_id or 0
    if st.session_state.get("chat_patient_key") != active_key:
        st.session_state.chat_patient_key = active_key
        st.session_state.chat_messages = []
        if patient_id:
            saved = reversed(get_patient_consultations(patient_id, limit=10))
            for item in saved:
                st.session_state.chat_messages.extend(
                    [
                        {"role": "user", "content": item.user_query},
                        {"role": "assistant", "content": item.assistant_response, "mode": "saved", "sources": [], "agent_status": []},
                    ]
                )
    for message in st.session_state.get("chat_messages", []):
        with st.chat_message(message["role"]):
            if message.get("mode") == "demo":
                st.warning("DEMO MODE · fixed sample text · no AI model generated this response")
            elif message.get("mode") == "unavailable":
                st.error("Local model unavailable")
            st.markdown(message["content"])
            if message["role"] == "assistant":
                with st.expander("Agent execution and sources"):
                    if message.get("agent_status"):
                        for item in message["agent_status"]:
                            st.write(f"**{item['agent']}** · {item['status']} · {item['detail']}")
                    render_sources(message.get("sources", []))

    question = st.chat_input("Ask a general health question")
    if question:
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Running the three local workflow agents..."):
                try:
                    result = run_assistant(question, patient_id=patient_id, demo_mode=demo_mode)
                except ValueError as exc:
                    st.error(str(exc))
                    st.stop()
            if result["response_mode"] == "demo":
                st.warning("DEMO MODE · fixed sample text · no AI model generated this response")
            elif result["response_mode"] == "unavailable":
                st.error("Local model unavailable. No paid or remote API was contacted.")
            elif result["response_mode"] == "guarded":
                st.warning("The response was withheld by the prototype's medical-safety filter.")
            elif result["response_mode"] == "emergency":
                st.error("Emergency safety check")
            st.markdown(result["answer"])
            with st.expander("Agent execution and sources", expanded=True):
                if result["agent_status"]:
                    for item in result["agent_status"]:
                        st.write(f"**{item['agent']}** · {item['status']} · {item['detail']}")
                render_sources(result.get("retrieved_documents", []))
        st.session_state.chat_messages.extend(
            [
                {"role": "user", "content": question},
                {
                    "role": "assistant",
                    "content": result["answer"],
                    "mode": result["response_mode"],
                    "sources": result.get("retrieved_documents", []),
                    "agent_status": result.get("agent_status", []),
                },
            ]
        )
        if save_history and patient_id and result["response_mode"] != "emergency":
            from database.db import save_consultation

            try:
                save_consultation(patient_id, question, result["answer"])
                st.toast("Consultation saved to the selected patient profile.")
            except Exception as exc:
                st.error(f"Could not save consultation: {exc}")

elif page == "Patient profile":
    st.subheader("Patient profile")
    st.markdown('<div class="mm-note">Profile details are stored on this device when you save.</div>', unsafe_allow_html=True)
    current = selected_patient
    with st.form("patient_profile"):
        name = st.text_input("Name", value=current.name if current else "")
        age_known = st.checkbox("Record age", value=current.age is not None if current else False)
        age = st.number_input("Age", min_value=0, max_value=125, value=current.age or 18 if current else 18, disabled=not age_known)
        medical_history = st.text_area("Medical history", value=current.medical_history if current else "")
        allergies = st.text_area("Reported allergies", value=current.allergies if current else "")
        medications = st.text_area("Reported medications", value=current.medications if current else "")
        submitted = st.form_submit_button("Save profile", type="primary")
    if submitted:
        try:
            values = {
                "name": name,
                "age": int(age) if age_known else None,
                "medical_history": medical_history,
                "allergies": allergies,
                "medications": medications,
            }
            if current:
                update_patient(current.id, **values)
            else:
                create_patient(**values)
            st.success("Profile saved locally.")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
    if current:
        st.markdown("### Previous consultations")
        consultations = get_patient_consultations(current.id, limit=20)
        if not consultations:
            st.caption("No consultations have been saved for this profile.")
        for item in consultations:
            with st.expander(f"{item.created_at:%Y-%m-%d %H:%M} · {item.user_query[:80]}"):
                st.markdown(f"**Question:** {item.user_query}")
                st.markdown(item.assistant_response)

else:
    st.subheader("Local knowledge base")
    try:
        documents = load_documents()
        st.caption(f"{len(documents)} bundled educational references · indexed chunks are stored under data/chroma")
        categories = sorted({item["category"] for item in documents})
        category = st.selectbox("Category", ["All"] + categories)
        filtered = [item for item in documents if category == "All" or item["category"] == category]
        search = st.text_input("Find a reference")
        if search:
            filtered = [item for item in filtered if search.lower() in f"{item['title']} {item['description']} {item['content']}".lower()]
        for item in filtered:
            with st.expander(f"{item['title']} · {item['category']}"):
                st.write(item["description"])
                st.write(item["content"])
                st.markdown(f"Source: [{item['source']['name']}]({item['source']['url']})")
        try:
            indexed_count = get_collection().count()
            st.caption(f"Currently indexed: {indexed_count} text chunks")
        except Exception as exc:
            st.warning(f"Local index status unavailable: {exc}")
        st.markdown("### Try local retrieval")
        query = st.text_input("Search the reference set", key="knowledge_query")
        if query:
            with st.spinner("Searching local references..."):
                try:
                    matches = retrieve(query, top_k=3)
                    if not matches:
                        st.info("No matching references were found.")
                    render_sources(matches)
                    for match in matches:
                        st.write(match["text"])
                except Exception as exc:
                    st.error(str(exc))
    except Exception as exc:
        st.error(f"Could not load the bundled knowledge files: {exc}")