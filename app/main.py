
import logging

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from app.auth import get_current_user
from app.rag_pipeline import answer_question


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")


app = FastAPI(
    title="Role-Based RAG API",
    description="Secure Student, Trainer and Admin RAG Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ais-dev-dxs3mqxkzscr4aepkuoh6v-962756732360.asia-southeast1.run.app",
        "https://ais-pre-dxs3mqxkzscr4aepkuoh6v-962756732360.asia-southeast1.run.app",
        "http://localhost:3000",
        "https://ai-student-learning-career-success-platform.ai.studio",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
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

    logger.info("Authentication check started")

    user = get_current_user(credentials.credentials)

    logger.info("Authentication successful. Role: %s", user["role"])

    return user


@app.post("/chat")
def chat(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    logger.info("POST /chat received")

    if credentials is None:
        logger.warning("Chat request rejected: Bearer token missing")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is required."
        )

    logger.info("Chat authentication started")

    user = get_current_user(credentials.credentials)
    role = user["role"]

    logger.info("Chat authentication successful. Role: %s", role)
    logger.info("RAG pipeline execution started")

    try:
        answer = answer_question(
            question=request.question,
            role=role,
            access_token=credentials.credentials
        )

        logger.info("RAG pipeline completed successfully")

        return {
            "user_id": user["user_id"],
            "role": role,
            "question": request.question,
            "answer": answer
        }

    except (ValueError, FileNotFoundError) as error:
        logger.exception("RAG validation failed")

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
