# Role-Based RAG Backend

## AI Student Learning & Career Success Platform

A secure, role-based Retrieval-Augmented Generation (RAG) backend designed to provide contextual AI assistance for Students, Trainers, and Admins.

## 1. Project Overview

This project implements a Role-Based RAG system using FastAPI, LangChain, Groq, HuggingFace embeddings, and Supabase pgvector.

The system authenticates users, identifies their roles, retrieves relevant information from role-specific knowledge bases, and generates context-aware answers using an LLM.

## 2. Problem Statement

Students, Trainers, and Admins require different types of information from the AI Student Learning & Career Success Platform.

A common chatbot may expose irrelevant information across user roles. This backend addresses that challenge through role-based authentication and document retrieval.

## 3. Key Features

- JWT-based user authentication.
- Role identification using Supabase user profiles.
- Separate Student, Trainer, and Admin knowledge bases.
- Document loading from PDF and DOCX files.
- Text chunking and embedding generation.
- Vector similarity search using Supabase pgvector.
- Context-based answer generation using Groq.
- REST API development using FastAPI.

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| Supabase | Authentication and database |
| PostgreSQL | Relational database |
| pgvector | Vector similarity search |
| LangChain | RAG pipeline orchestration |
| HuggingFace | Text embeddings |
| Groq | LLM inference |
| Git & GitHub | Version control |

## 5. System Architecture

1. User submits a question with a Supabase access token.
2. FastAPI validates the JWT.
3. The authenticated user's role is retrieved from Supabase.
4. HuggingFace generates a query embedding.
5. Supabase pgvector retrieves relevant documents for that role.
6. Retrieved context and the question are passed to the Groq LLM.
7. The generated answer is returned through the API.

## 6. Project Structure

```text
AI_career/
│
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── ingest.py
│   ├── main.py
│   ├── rag_pipeline.py
│   ├── security.py
│   └── supabase_client.py
│
├── data/
│   ├── student/
│   ├── trainer/
│   └── admin/
│
├── .env.example
├── .gitignore
└── requirements.txt
```

Note: The `data/` directory contains local knowledge-base documents and is excluded from Git.

## 7. Installation

Clone the repository:

```bash
git clone https://github.com/chebolusatya2005-prog/Phase_II_Role_Based_RAG.git
cd Phase_II_Role_Based_RAG
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```cmd
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 8. Environment Configuration

Create a `.env` file in the project root using `.env.example` as a reference.

Configure the following variables:

```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_publishable_key
SUPABASE_SERVICE_ROLE_KEY=your_backend_secret_key
LLM_MODEL=openai/gpt-oss-120b
```

Never commit `.env` or expose API keys and service-role credentials.

## 9. Database Setup

The project uses Supabase PostgreSQL with the pgvector extension.

Required database components:

- `public.users` – authenticated user profiles and roles.
- `public.rag_documents` – role-specific knowledge chunks and embeddings.
- `public.match_rag_documents` – vector similarity search function.

The RAG documents table stores:
- Role
- Document content
- Metadata
- Vector embeddings

Row Level Security (RLS) and role-based policies help restrict document access.

The database schema and policies must be configured in the Supabase project before running ingestion and retrieval.

## 10. Document Ingestion

Place the knowledge documents in the appropriate local folders:

```text
data/student/
data/trainer/
data/admin/
```

Supported formats:
- PDF
- DOCX

Run ingestion:

```bash
python -m app.ingest
```

The ingestion process loads documents, splits text into chunks, generates embeddings, and stores them in Supabase pgvector.

## 11. Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Open Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## 12. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API health/message |
| GET | `/auth/me` | Retrieve authenticated user information |
| POST | `/chat` | Ask role-specific RAG questions |

The `/auth/me` and `/chat` endpoints require a valid Supabase Bearer access token.

## 13. Testing Results

The following initial API tests were completed successfully:

| User Role | Test | Result |
|---|---|---|
| Student | Role-specific question | HTTP 200 |
| Trainer | Role-specific question | HTTP 200 |
| Admin | Role-specific question | HTTP 200 |
| Admin | Authentication via `/auth/me` | HTTP 200 |

These results confirm successful initial role-based retrieval and authentication tests. They do not represent exhaustive security testing.

## 14. Security Considerations

- Validate user authentication before processing requests.
- Retrieve the role from the authenticated Supabase profile.
- Apply role-specific document retrieval.
- Use Row Level Security for database access.
- Keep service-role credentials restricted to trusted backend operations.
- Never expose API keys, passwords, or JWT tokens.

## 15. Future Improvements

- Expanded role-based authorization testing.
- Improved error handling and logging.
- Automated testing.
- Production deployment.
- Performance optimization.
- Monitoring and evaluation of RAG responses.

---

**Project:** AI Student Learning & Career Success Platform  
**Module:** Phase II – Role-Based RAG Backend  
**Repository:** https://github.com/chebolusatya2005-prog/Phase_II_Role_Based_RAG
