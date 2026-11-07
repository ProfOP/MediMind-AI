from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "presentation_assets"
OUTPUT = ROOT / "MediMind_AI_Project_Report.pdf"
WIDTH, HEIGHT = landscape(A4)
MARGIN = 42

INK = colors.HexColor("#203B36")
MUTED = colors.HexColor("#60736E")
TEAL = colors.HexColor("#167C72")
PALE = colors.HexColor("#F5F8F6")
MINT = colors.HexColor("#EAF4EF")
LINE = colors.HexColor("#DCE7E2")
CORAL = colors.HexColor("#C65E47")
WHITE = colors.white


def draw_background(pdf, number, section, title=None, subtitle=None):
    pdf.setFillColor(PALE)
    pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    pdf.setFillColor(TEAL)
    pdf.rect(0, HEIGHT - 7, WIDTH, 7, fill=1, stroke=0)
    pdf.setFillColor(TEAL)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(MARGIN, HEIGHT - 29, section.upper())
    if title:
        pdf.setFillColor(INK)
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawString(MARGIN, HEIGHT - 61, title)
    if subtitle:
        pdf.setFillColor(MUTED)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(MARGIN, HEIGHT - 80, subtitle)
    pdf.setStrokeColor(LINE)
    pdf.line(MARGIN, 28, WIDTH - MARGIN, 28)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(MARGIN, 15, "MEDIMIND AI  ·  LOCAL EDUCATIONAL PROTOTYPE")
    pdf.drawRightString(WIDTH - MARGIN, 15, f"{number:02d} / 12")


def paragraph(pdf, text, x, top, width, size=11, leading=None, color=INK):
    style = ParagraphStyle(
        name=f"p-{size}-{color.hexval()}",
        fontName="Helvetica",
        fontSize=size,
        leading=leading or size * 1.42,
        textColor=color,
        spaceAfter=0,
        splitLongWords=1,
    )
    item = Paragraph(text, style)
    _, height = item.wrap(width, HEIGHT)
    item.drawOn(pdf, x, top - height)
    return top - height


def bullets(pdf, items, x, top, width, size=10.5, gap=9, color=INK):
    y = top
    for item in items:
        y = paragraph(pdf, f'<font color="{TEAL.hexval()}">•</font>  {item}', x, y, width, size, size * 1.42, color)
        y -= gap
    return y


def label(pdf, text, x, y, color=TEAL):
    pdf.setFillColor(color)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(x, y, text.upper())


def stat(pdf, x, y, w, heading, detail):
    pdf.setFillColor(WHITE)
    pdf.setStrokeColor(LINE)
    pdf.roundRect(x, y, w, 62, 5, fill=1, stroke=1)
    pdf.setFillColor(TEAL)
    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawString(x + 13, y + 34, heading)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 8.5)
    pdf.drawString(x + 13, y + 17, detail)


def screenshot_box(pdf, path, x, y, w, h, caption):
    pdf.setFillColor(WHITE)
    pdf.setStrokeColor(LINE)
    pdf.roundRect(x, y, w, h, 5, fill=1, stroke=1)
    inner_x = x + 8
    inner_y = y + 25
    inner_w = w - 16
    inner_h = h - 33
    image = ImageReader(str(path))
    image_w, image_h = image.getSize()
    scale = min(inner_w / image_w, inner_h / image_h)
    draw_w = image_w * scale
    draw_h = image_h * scale
    pdf.drawImage(
        image,
        inner_x + (inner_w - draw_w) / 2,
        inner_y + (inner_h - draw_h) / 2,
        width=draw_w,
        height=draw_h,
        mask="auto",
    )
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(x + 10, y + 8, caption)


def node(pdf, x, y, w, h, title, detail, fill=WHITE, accent=TEAL):
    pdf.setFillColor(fill)
    pdf.setStrokeColor(LINE)
    pdf.roundRect(x, y, w, h, 6, fill=1, stroke=1)
    pdf.setFillColor(accent)
    pdf.rect(x, y + h - 4, w, 4, fill=1, stroke=0)
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x + 12, y + h - 22, title)
    paragraph(pdf, detail, x + 12, y + h - 31, w - 24, 8.5, 11, MUTED)


def draw_cover(pdf):
    pdf.setFillColor(PALE)
    pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    pdf.setFillColor(MINT)
    pdf.rect(WIDTH * 0.62, 0, WIDTH * 0.38, HEIGHT, fill=1, stroke=0)
    pdf.setFillColor(TEAL)
    pdf.rect(MARGIN, HEIGHT - 42, 34, 4, fill=1, stroke=0)
    label(pdf, "College project overview · 2026", MARGIN, HEIGHT - 63)
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 34)
    pdf.drawString(MARGIN, HEIGHT - 118, "MediMind AI")
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 16)
    pdf.drawString(MARGIN, HEIGHT - 147, "A local, agentic medical-information prototype")
    y = paragraph(
        pdf,
        "A proof of concept for educational health information, source retrieval, and patient-scoped memory. "
        "Designed to demonstrate local AI components without paid model APIs.",
        MARGIN,
        HEIGHT - 185,
        315,
        12,
        18,
    )
    bullets(
        pdf,
        ["Three sequential LangGraph agents", "Local ChromaDB retrieval with source links", "SQLite profile and consultation history", "Streamlit interface with an explicitly labelled demo mode"],
        MARGIN,
        y - 25,
        320,
        10.5,
        9,
    )
    screenshot_box(
        pdf,
        ASSETS / "01_assistant_demo.png",
        390,
        116,
        410,
        340,
        "Captured from the running local app · response explicitly marked as demo text",
    )
    pdf.setStrokeColor(LINE)
    pdf.line(MARGIN, 28, WIDTH - MARGIN, 28)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(MARGIN, 15, "EDUCATIONAL PROTOTYPE · NOT FOR DIAGNOSIS OR TREATMENT")
    pdf.drawRightString(WIDTH - MARGIN, 15, "01 / 12")
    pdf.showPage()


def build_report():
    pdf = canvas.Canvas(str(OUTPUT), pagesize=(WIDTH, HEIGHT), pageCompression=1)
    pdf.setTitle("MediMind AI Project Report")
    pdf.setAuthor("MediMind AI project team")

    draw_cover(pdf)

    draw_background(pdf, 2, "01 · Product", "What MediMind AI is", "A compact college showcase of agentic information retrieval with local patient memory.")
    paragraph(
        pdf,
        "MediMind AI is a local-first educational assistant prototype. A user asks a general health-information question; "
        "the application can retrieve relevant excerpts from a small bundled reference set and, when Ollama is running, "
        "ask a local language model to form a cautious plain-language response.",
        MARGIN,
        HEIGHT - 116,
        470,
        12,
        18,
    )
    label(pdf, "Core capabilities", MARGIN, HEIGHT - 218)
    bullets(pdf, [
        "Chat UI with patient selection, agent status, and source references.",
        "Three sequential agents with explicit shared workflow state.",
        "Local semantic retrieval using sentence embeddings and ChromaDB.",
        "SQLite patient profiles and saved consultations, isolated by patient ID.",
        "Fixed-response demo mode when a live model is unavailable.",
    ], MARGIN, HEIGHT - 238, 470, 10.5, 8)
    stat(pdf, 548, 345, 115, "3", "workflow agents")
    stat(pdf, 676, 345, 124, "10", "bundled references")
    stat(pdf, 548, 265, 115, "3", "UI pages")
    stat(pdf, 676, 265, 124, "0", "paid AI APIs")
    paragraph(pdf, "Intended for a classroom demonstration and code exploration. It is not a clinical product.", 548, 228, 250, 10, 14, MUTED)
    pdf.showPage()

    draw_background(pdf, 3, "02 · User experience", "Medical assistant", "A chat-oriented interface keeps the question, result, execution state, and sources together.")
    screenshot_box(pdf, ASSETS / "01_assistant_demo.png", MARGIN, 90, 468, 392, "Assistant page captured in labelled demo mode")
    label(pdf, "What the screen demonstrates", 542, HEIGHT - 125)
    bullets(pdf, [
        "The response is clearly marked as fixed demo text, not live model output.",
        "Agent execution status is expandable for a concise, explainable trace.",
        "Retrieved references are displayed with titles and source names.",
        "Patient selection and history-saving confirmation are optional controls.",
    ], 542, HEIGHT - 147, 250, 10.5, 11)
    paragraph(pdf, "When demo mode is off and Ollama is unavailable, the app shows a local-service error and does not switch to a cloud API.", 542, 280, 250, 10, 14, CORAL)
    pdf.showPage()

    draw_background(pdf, 4, "03 · Orchestration", "Three-agent workflow", "A small sequential graph keeps responsibilities visible and easy to explain.")
    node(pdf, 48, 304, 155, 112, "1 · Patient Context", "Reads only the selected profile, reported allergies/medications, and recent consultations.", MINT)
    node(pdf, 250, 304, 155, 112, "2 · Medical Knowledge", "Retrieves up to three relevant chunks from the local Chroma collection.", WHITE)
    node(pdf, 452, 304, 155, 112, "3 · Medical Response", "Uses local Ollama when available; follows cautious educational instructions.", MINT)
    pdf.setStrokeColor(TEAL)
    pdf.setLineWidth(2)
    for x1, x2 in ((203, 250), (405, 452)):
        pdf.line(x1 + 4, 360, x2 - 7, 360)
        pdf.line(x2 - 12, 365, x2 - 7, 360)
        pdf.line(x2 - 12, 355, x2 - 7, 360)
    node(pdf, 655, 304, 140, 112, "Final answer", "Educational response, uncertainty, source list, and agent status.", WHITE)
    pdf.line(607, 360, 648, 360)
    pdf.line(643, 365, 648, 360)
    pdf.line(643, 355, 648, 360)
    label(pdf, "Before the graph", 48, 250, CORAL)
    paragraph(pdf, "A basic emergency-keyword check runs first. Obvious emergency indicators bypass routine processing and return an urgent-care message.", 48, 230, 340, 11, 16)
    label(pdf, "Shared state", 445, 250)
    paragraph(pdf, "The graph passes the question, selected patient ID, patient context, retrieved documents, response mode, answer, and per-agent status.", 445, 230, 345, 11, 16)
    pdf.showPage()

    draw_background(pdf, 5, "04 · Product tour", "Patient profile and memory", "Memory is deliberately simple: profile fields plus a chronological consultation table.")
    screenshot_box(pdf, ASSETS / "02_patient_profile.png", MARGIN, 90, 468, 392, "Patient profile form · captured with no patient information")
    label(pdf, "Stored locally in SQLite", 542, HEIGHT - 125)
    bullets(pdf, [
        "Patient name and optional age.",
        "Medical history, reported allergies, and reported medications.",
        "Consultation question, assistant response, and timestamp.",
        "Recent consultations are included as context only for that selected patient.",
    ], 542, HEIGHT - 147, 250, 10.5, 11)
    paragraph(pdf, "The user confirms saving by enabling the history checkbox. Profile details are stored only after the profile form is submitted.", 542, 285, 250, 10, 14, MUTED)
    pdf.showPage()

    draw_background(pdf, 6, "05 · Retrieval", "Knowledge base and sources", "Bundled JSON references keep the demonstration independent of external medical datasets.")
    screenshot_box(pdf, ASSETS / "03_knowledge_base_rag.png", 402, 88, 398, 394, "Knowledge Base page · local query with top-three source results")
    label(pdf, "Included in this build", MARGIN, HEIGHT - 125)
    bullets(pdf, [
        "10 short educational documents across conditions, symptoms, FAQs, and medication safety.",
        "Source metadata includes document title, category, source name, and URL.",
        "Searchable library plus a retrieval demonstration in the UI.",
        "Verified query: seasonal allergies / pollen returned three matches, led by MedlinePlus allergic rhinitis.",
    ], MARGIN, HEIGHT - 147, 335, 10.5, 10)
    paragraph(pdf, "The bundled set is intentionally small and is not a complete or clinically reviewed medical reference library.", MARGIN, 188, 335, 10, 14, CORAL)
    pdf.showPage()

    draw_background(pdf, 7, "06 · RAG pipeline", "How local retrieval works", "The first embedding-model download is the only expected model-cache setup step for retrieval.")
    steps = [
        ("JSON", "Load bundled records"),
        ("CHUNK", "Split searchable text"),
        ("EMBED", "MiniLM vectors locally"),
        ("INDEX", "Persist in ChromaDB"),
        ("TOP 3", "Return text + sources"),
    ]
    x = 48
    for idx, (tag, detail) in enumerate(steps):
        pdf.setFillColor(MINT if idx % 2 == 0 else WHITE)
        pdf.setStrokeColor(LINE)
        pdf.roundRect(x, 327, 137, 82, 6, fill=1, stroke=1)
        pdf.setFillColor(TEAL)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(x + 14, 378, tag)
        paragraph(pdf, detail, x + 14, 365, 108, 9.5, 12, MUTED)
        if idx < len(steps) - 1:
            pdf.setStrokeColor(TEAL)
            pdf.line(x + 137, 368, x + 151, 368)
        x += 151
    stat(pdf, 48, 210, 170, "10", "indexed text chunks")
    stat(pdf, 238, 210, 235, "MiniLM", "all-MiniLM-L6-v2 · local embeddings")
    stat(pdf, 493, 210, 300, "ChromaDB", "persistent project-local collection")
    paragraph(pdf, "Observed in the local smoke test: model downloaded to the project cache, 10 chunks indexed, and top-three references returned with source metadata.", 48, 177, 720, 11, 16)
    pdf.showPage()

    draw_background(pdf, 8, "07 · Local-first design", "Data boundaries", "Application packages, model caches, vector store, and user records are rooted in this project folder.")
    label(pdf, "Project-local storage", 48, HEIGHT - 125)
    bullets(pdf, [
        "Python packages are installed in the workspace .venv.",
        "SQLite database: data/medimind.sqlite3.",
        "Chroma collection: data/chroma/.",
        "Embedding-model cache: data/models/.",
        "Streamlit home, cache, and temporary files are redirected to project-local folders at launch.",
    ], 48, HEIGHT - 148, 340, 10.5, 9)
    label(pdf, "Network behavior", 445, HEIGHT - 125)
    bullets(pdf, [
        "Ollama requests are restricted to localhost.",
        "No paid LLM or embedding API is configured.",
        "The first embedding-model setup needs internet; cached retrieval can work offline afterward.",
        "Ollama itself is optional for the labelled demo mode and is not installed in the verified environment.",
    ], 445, HEIGHT - 148, 345, 10.5, 11)
    paragraph(pdf, "Local storage reduces external data transfer, but this prototype is not a hardened system for real patient records. Use synthetic data for demonstrations.", 48, 162, 742, 10.5, 15, CORAL)
    pdf.showPage()

    draw_background(pdf, 9, "08 · Safety", "Guardrails and limitations", "The system is designed to inform and demonstrate, not to diagnose or direct treatment.")
    label(pdf, "Implemented safeguards", 48, HEIGHT - 125)
    bullets(pdf, [
        "Emergency keyword screen runs before the graph and advises contacting local emergency services.",
        "Prompt instructions prohibit diagnoses, prescriptions, dosage recommendations, and medication changes.",
        "A response filter withholds some obvious diagnostic or dosage instructions from generated text.",
        "Missing patient facts are marked as missing instead of being inferred.",
        "The required educational disclaimer is visible in the interface.",
        "Demo responses are fixed text and clearly identified as non-AI output.",
    ], 48, HEIGHT - 148, 440, 10.5, 8)
    pdf.setFillColor(colors.HexColor("#FFF8F4"))
    pdf.setStrokeColor(colors.HexColor("#E9C8BB"))
    pdf.roundRect(530, 210, 264, 210, 6, fill=1, stroke=1)
    label(pdf, "Important limitation", 550, 392, CORAL)
    paragraph(pdf, "Keyword checks and output filters are basic safeguards, not clinical validation. They can miss emergencies or unsafe wording. The local model may still produce inaccurate information.", 550, 369, 220, 11, 16)
    paragraph(pdf, "Never rely on MediMind for medical decisions. In an emergency, contact local emergency services.", 550, 277, 220, 10, 14, CORAL)
    pdf.showPage()

    draw_background(pdf, 10, "09 · Technology", "What runs locally", "A lightweight local chat model is configured; retrieval uses a separate small embedding model.")
    stats = [
        ("Python", "3.11.7 in .venv"),
        ("Streamlit", "UI · 1.66.1"),
        ("LangGraph", "workflow · 1.2.19"),
        ("ChromaDB", "vector store · 1.5.9"),
        ("Sentence Transformers", "embeddings · 5.7.0"),
        ("SQLAlchemy + SQLite", "patient memory · 2.1.6"),
    ]
    positions = [(48, 348), (300, 348), (552, 348), (48, 257), (300, 257), (552, 257)]
    for (heading, detail), (x, y) in zip(stats, positions):
        stat(pdf, x, y, 225, heading, detail)
    label(pdf, "Chat model status", 48, 218)
    paragraph(pdf, "Default Ollama model: smollm2:360m. This was selected for low resource use. Ollama is not installed here, so live generation has not been verified. The app reports an unavailable error rather than falling back to an external service.", 48, 198, 725, 11, 16)
    pdf.showPage()

    draw_background(pdf, 11, "10 · Verification", "What was tested", "A distinction between automated checks, manual smoke tests, and unverified live-model behavior.")
    stat(pdf, 48, 360, 170, "9 / 9", "automated tests passed")
    stat(pdf, 238, 360, 170, "3 / 3", "agents reported in workflow test")
    stat(pdf, 428, 360, 170, "10", "RAG chunks indexed")
    stat(pdf, 618, 360, 175, "3", "top references returned")
    label(pdf, "Verified", 48, 321)
    bullets(pdf, [
        "SQLite profile creation, retrieval, isolation, and consultation persistence.",
        "JSON loading, chunking, and Chroma retrieval with mocked embeddings in tests.",
        "Emergency short-circuit, three-agent workflow, demo mode, and local-host restriction.",
        "Manual browser checks of assistant, profile, and knowledge-base pages.",
        "Real local MiniLM retrieval with source attribution.",
    ], 48, 300, 360, 10.2, 7)
    label(pdf, "Not verified / not installed", 445, 321, CORAL)
    bullets(pdf, [
        "Live Ollama inference: Ollama runtime and model were absent.",
        "Clinical quality or completeness: this is a small educational corpus, not clinical validation.",
        "The exact emergency keyword list is not a replacement for triage.",
    ], 445, 300, 345, 10.2, 10, CORAL)
    pdf.showPage()

    draw_background(pdf, 12, "11 · Demonstration", "Run locally and next steps", "A short classroom walkthrough can demonstrate the architecture without model service access.")
    label(pdf, "Demo sequence", 48, HEIGHT - 125)
    bullets(pdf, [
        "Launch the app from the project .venv.",
        "Turn on labelled demo mode and submit a general question.",
        "Expand agent status and source references.",
        "Open Patient profile; create synthetic data and explicitly confirm history saving.",
        "Open Knowledge Base; filter a topic and run a local retrieval query.",
        "Try an emergency keyword to show the pre-graph safety response.",
    ], 48, HEIGHT - 148, 400, 10.5, 9)
    label(pdf, "If enabling live generation", 492, HEIGHT - 125)
    bullets(pdf, [
        "Install Ollama separately and keep its model directory under data/ollama/models.",
        "Pull the configured small model (smollm2:360m) or set OLLAMA_MODEL to another local model.",
        "Start Streamlit with project-local HOME, cache, and temp directories as documented in README.md.",
    ], 492, HEIGHT - 148, 300, 10.5, 11)
    pdf.setFillColor(MINT)
    pdf.roundRect(48, 88, 744, 67, 6, fill=1, stroke=0)
    paragraph(pdf, "Bottom line: MediMind demonstrates local orchestration, retrieval, persistence, and a cautious UI. It is a teaching prototype, not a medical service.", 66, 138, 705, 11, 16, INK)
    pdf.showPage()

    pdf.save()
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    build_report()