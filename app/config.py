
import os
from pathlib import Path

from dotenv import load_dotenv


# 1. Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


# 2. Load environment variables from .env
load_dotenv(BASE_DIR / ".env")


# 3. Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# 4. Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Backend-only key used for document ingestion.
# Never expose this key in frontend code.
SUPABASE_SERVICE_ROLE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY"
)


# 5. HuggingFace embedding model
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)


# 6. Groq LLM configuration
LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "openai/gpt-oss-120b"
)


# 7. Data directories
DATA_DIR = BASE_DIR / "data"

STUDENT_DATA_DIR = DATA_DIR / "student"

TRAINER_DATA_DIR = DATA_DIR / "trainer"

ADMIN_DATA_DIR = DATA_DIR / "admin"


# 8. FAISS vector database directories
VECTORSTORE_DIR = BASE_DIR / "vectorstores"

STUDENT_VECTORSTORE = VECTORSTORE_DIR / "student"

TRAINER_VECTORSTORE = VECTORSTORE_DIR / "trainer"

ADMIN_VECTORSTORE = VECTORSTORE_DIR / "admin"


# 9. Document processing configuration
CHUNK_SIZE = 800

CHUNK_OVERLAP = 150


# 10. Create vectorstore directories automatically
for directory in [
    STUDENT_VECTORSTORE,
    TRAINER_VECTORSTORE,
    ADMIN_VECTORSTORE
]:
    directory.mkdir(parents=True, exist_ok=True)
