
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


MATCH_COUNT = 4


def answer_question(
    question: str,
    role: str,
    access_token: str
):
    """Retrieve role-specific documents from Supabase and generate an answer."""

    # 1. Validate role
    role = role.lower().strip()

    if role not in ["student", "trainer", "admin"]:
        raise ValueError("Invalid user role")

    if not access_token:
        raise ValueError("User access token is required")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase configuration is missing")

    if not GROQ_API_KEY:
        raise ValueError("Groq API key is missing")

    # 2. Create a Supabase client for this authenticated request
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

    # Attach the logged-in user's JWT.
    # Supabase RLS will control which documents can be retrieved.
    supabase.postgrest.auth(access_token)

    # 3. Initialize embedding model
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    # 4. Convert user question into an embedding
    query_embedding = embeddings.embed_query(question)

    # 5. Search relevant documents in Supabase pgvector
    result = supabase.rpc(
        "match_rag_documents",
        {
            "query_embedding": query_embedding,
            "match_count": MATCH_COUNT,
            "filter_role": role
        }
    ).execute()

    retrieved_docs = result.data

    if not retrieved_docs:
        return "I could not find relevant information in your knowledge base."

    # 6. Prepare context from retrieved documents
    context_parts = []

    for document in retrieved_docs:
        content = document.get("content", "").strip()

        if content:
            context_parts.append(content)

    context = "\n\n".join(context_parts).strip()

    if not context:
        return "I could not find relevant information in your knowledge base."

    # 7. Create prompt
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

    # 8. Initialize Groq LLM
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=0
    )

    # 9. Generate answer
    chain = prompt | llm

    response = chain.invoke({
        "context": context,
        "question": question,
        "role": role
    })

    return response.content
