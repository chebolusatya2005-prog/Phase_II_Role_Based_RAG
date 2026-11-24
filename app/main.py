import logging
logger=logging.getLogger(__name__)
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from app.auth import get_current_user
from app.rag_pipeline import answer_question


app = FastAPI(
    title="Role-Based RAG API",
    description="Secure Student, Trainer and Admin RAG Backend",
    version="1.0.0"
)

bearer_scheme = HTTPBearer(auto_error=False)


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000
    )


@app.get("/")
def home():
    return {
        "message": "Role-Based RAG API is running!"
    }


@app.get("/auth/me")
def current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is required."
        )

    return get_current_user(credentials.credentials)


@app.post("/chat")
def chat(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    # 1. Verify authentication
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is required."
        )

    # 2. Get authenticated user and verified role
    user = get_current_user(credentials.credentials)
    role = user["role"]

        # 3. Generate role-specific RAG answer
    try:
        answer = answer_question(
    question=request.question,
    role=role,
    access_token=credentials.credentials
)
        return {
            "user_id": user["user_id"],
            "role": role,
            "question": request.question,
            "answer": answer
        }

    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )

    except Exception:
        logger.exception("RAG chat generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating the answer."
        )