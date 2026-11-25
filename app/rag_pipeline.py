
import logging
import time
from functools import lru_cache

from supabase import create_client
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate

from app.config import (
    EMBEDDING_MODEL,
    LLM_MODEL,
    GROQ_API_KEY,
    SUPABASE_URL,
    SUPABASE_KEY,
)


# Logging configuration
logger = logging.getLogger(__name__)

MATCH_COUNT = 4


# Load the embedding model only once and reuse it.
@lru_cache(maxsize=1)
def get_embeddings():
    logger.info("Loading HuggingFace embedding model: %s", EMBEDDING_MODEL)

    start_time = time.perf_counter()

    model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    logger.info(
        "Embedding model loaded in %.2f seconds",
        time.perf_counter() - start_time
    )

    return model


def answer_question(
    question: str,
    role: str,
    access_token: str
):
    """Retrieve role-specific documents and generate an answer."""

    # 1. Validate inputs
    role = role.lower().strip()

    if role not in ["student", "trainer", "admin"]:
        raise ValueError("Invalid user role")

    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    if not access_token:
        raise ValueError("User access token is required")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase configuration is missing")

    if not GROQ_API_KEY:
        raise ValueError("Groq API key is missing")

    logger.info("Starting RAG request for role: %s", role)

    # 2. Create authenticated Supabase client
    stage_start = time.perf_counter()

    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

    supabase.postgrest.auth(access_token)

    logger.info(
        "Supabase client initialized in %.2f seconds",
        time.perf_counter() - stage_start
    )

    # 3. Generate question embedding
    try:
        stage_start = time.perf_counter()

        embeddings = get_embeddings()

        query_embedding = embeddings.embed_query(question)

        logger.info(
            "Question embedding generated in %.2f seconds",
            time.perf_counter() - stage_start
        )

    except Exception:
        logger.exception("Question embedding generation failed")
        raise

    # 4. Retrieve role-specific documents from Supabase
    try:
        stage_start = time.perf_counter()

        result = supabase.rpc(
            "match_rag_documents",
            {
                "query_embedding": query_embedding,
                "match_count": MATCH_COUNT,
                "filter_role": role
            }
        ).execute()

        retrieved_docs = result.data or []

        logger.info(
            "Supabase retrieval completed in %.2f seconds. Documents: %d",
            time.perf_counter() - stage_start,
            len(retrieved_docs)
        )

    except Exception:
        logger.exception("Supabase document retrieval failed")
        raise

    if not retrieved_docs:
        return "I could not find relevant information in your knowledge base."

    # 5. Prepare retrieved context
    context_parts = []

    for document in retrieved_docs:
        content = document.get("content", "").strip()

        if content:
            context_parts.append(content)

    context = "\n\n".join(context_parts).strip()

    if not context:
        return "I could not find relevant information in your knowledge base."

    # 6. Create role-based prompt
    prompt = ChatPromptTemplate.from_template("""
    You are a role-based AI career assistant.

    The authenticated user's role is: {role}

    Answer the user's question using ONLY the provided context.

    Rules:
    - Do not invent facts.
    - Do not use information outside the context.
    - If the answer is not available, clearly say so.
    - Give a clear and helpful answer.
    - Keep the answer relevant to the user's role.

    Context:
    {context}

    User Question:
    {question}

    Answer:
    """)

    # 7. Initialize Groq LLM with a request timeout
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=0,
        timeout=30,
        max_retries=1
    )

    # 8. Generate answer
    try:
        stage_start = time.perf_counter()

        chain = prompt | llm

        response = chain.invoke({
            "context": context,
            "question": question,
            "role": role
        })

        logger.info(
            "Groq answer generated in %.2f seconds",
            time.perf_counter() - stage_start
        )

        logger.info("RAG request completed successfully")

        return response.content

    except Exception:
        logger.exception("Groq answer generation failed")
        raise
