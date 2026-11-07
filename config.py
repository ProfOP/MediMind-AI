import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"
MODEL_CACHE_DIR = DATA_DIR / "models"
CHROMA_DIR = DATA_DIR / "chroma"
DB_PATH = Path(os.getenv("MEDIMIND_DB_PATH", DATA_DIR / "medimind.sqlite3"))

for path in (DATA_DIR, MODEL_CACHE_DIR, CHROMA_DIR):
    path.mkdir(parents=True, exist_ok=True)

os.environ["HF_HOME"] = str(MODEL_CACHE_DIR / "huggingface")
os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(MODEL_CACHE_DIR / "sentence-transformers")
os.environ["TORCH_HOME"] = str(MODEL_CACHE_DIR / "torch")
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

EMBEDDING_MODEL = os.getenv("MEDIMIND_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "smollm2:360m")

DISCLAIMER = (
    "MediMind AI provides general healthcare information for educational purposes only. "
    "It does not provide medical diagnoses or prescribe treatments. Always consult a "
    "qualified healthcare professional for medical concerns. In an emergency, contact "
    "local emergency services."
)