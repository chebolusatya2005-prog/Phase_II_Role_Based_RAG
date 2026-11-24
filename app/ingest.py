
"""
Role-Based RAG Ingestion Pipeline.

Loads Student, Trainer, and Admin PDF/DOCX documents,
splits them into chunks, generates embeddings,
and stores them in Supabase pgvector.
"""

import json

from pathlib import Path
from supabase import create_client

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import (
    STUDENT_DATA_DIR,
    TRAINER_DATA_DIR,
    ADMIN_DATA_DIR,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)


BATCH_SIZE = 50


def load_documents(data_dir):
    """Load PDF and DOCX documents from a role-specific folder."""

    documents = []

    pdf_files = list(data_dir.glob("*.pdf"))
    docx_files = list(data_dir.glob("*.docx"))

    all_files = pdf_files + docx_files

    if not all_files:
        raise FileNotFoundError(
            f"No PDF or DOCX files found in: {data_dir}"
        )

    for file_path in all_files:

        print(f"Loading: {file_path.name}")

        if file_path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(file_path))
        else:
            loader = Docx2txtLoader(str(file_path))

        loaded_docs = loader.load()

        # Keep only the filename in metadata
        for document in loaded_docs:
            document.metadata["source"] = file_path.name

        documents.extend(loaded_docs)

    return documents


def create_supabase_store(role, data_dir, embeddings, supabase):
    """Generate document embeddings and store them in Supabase."""

    print(f"\nProcessing {role.upper()} documents")

    # 1. Load documents
    documents = load_documents(data_dir)

    print(f"Documents loaded: {len(documents)}")

    # 2. Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = text_splitter.split_documents(documents)

    if not chunks:
        raise ValueError(
            f"No text chunks generated for {role}"
        )

    print(f"Chunks created: {len(chunks)}")

    # 3. Generate embeddings
    texts = [chunk.page_content for chunk in chunks]

    vectors = embeddings.embed_documents(texts)

    print(f"Embeddings generated: {len(vectors)}")

    # 4. Prepare Supabase records
    rows = []

    for chunk, vector in zip(chunks, vectors):

        metadata = json.loads(
            json.dumps(chunk.metadata, default=str)
        )

        rows.append({
            "role": role,
            "content": chunk.page_content,
            "metadata": metadata,
            "embedding": vector
        })

    # 5. Delete old records for this role
    # This prevents duplicate records during re-ingestion.
    print(f"Replacing existing {role.upper()} records...")

    supabase.table("rag_documents").delete().eq(
        "role", role
    ).execute()

    # 6. Insert new records in batches
    for start in range(0, len(rows), BATCH_SIZE):

        batch = rows[start:start + BATCH_SIZE]

        supabase.table("rag_documents").insert(
            batch
        ).execute()

        uploaded = min(start + BATCH_SIZE, len(rows))

        print(
            f"{role.upper()}: Uploaded "
            f"{uploaded}/{len(rows)} chunks"
        )

    print(
        f"{role.upper()} documents stored successfully!"
    )


def main():
    """Ingest all three role-specific knowledge bases."""

    # 1. Validate Supabase configuration
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError(
            "Supabase URL or Service Role Key is missing. "
            "Check your Phase 2 .env file."
        )

    print("Starting Supabase RAG ingestion...")

    # 2. Connect to Supabase
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY
    )

    print("Supabase connection initialized.")

    # 3. Initialize embedding model
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    print("Embedding model initialized.")

    # 4. Process Student documents
    create_supabase_store(
        "student",
        STUDENT_DATA_DIR,
        embeddings,
        supabase
    )

    # 5. Process Trainer documents
    create_supabase_store(
        "trainer",
        TRAINER_DATA_DIR,
        embeddings,
        supabase
    )

    # 6. Process Admin documents
    create_supabase_store(
        "admin",
        ADMIN_DATA_DIR,
        embeddings,
        supabase
    )

    print("\nAll three role knowledge bases uploaded successfully!")

    print("Supabase RAG ingestion completed.")


if __name__ == "__main__":
    main()
