import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

# 3. API and Supabase configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY"
)

# Backend-only key for Supabase document ingestion
SUPABASE_SERVICE_ROLE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY"
)

# 4. HuggingFace embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# 5. LLM model configuration
LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "openai/gpt-oss-120b"
)

# 6. Data directories
DATA_DIR = BASE_DIR / "data"

STUDENT_DATA_DIR = DATA_DIR / "student"
TRAINER_DATA_DIR = DATA_DIR / "trainer"
ADMIN_DATA_DIR = DATA_DIR / "admin"

# 7. FAISS vector database directories
VECTORSTORE_DIR = BASE_DIR / "vectorstores"

STUDENT_VECTORSTORE = VECTORSTORE_DIR / "student"
TRAINER_VECTORSTORE = VECTORSTORE_DIR / "trainer"
ADMIN_VECTORSTORE = VECTORSTORE_DIR / "admin"

# 8. Document processing configuration
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# 9. Create vectorstore directories automatically
for directory in [
    STUDENT_VECTORSTORE,
    TRAINER_VECTORSTORE,
    ADMIN_VECTORSTORE
]:
    directory.mkdir(parents=True, exist_ok=True)
