from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5:1.5b"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"


settings = Settings()


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=30)


class ChatResponse(BaseModel):
    reply: str


app = FastAPI(title="Homework6 AI Chat API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a concise assistant for a compiler design course. "
                "Prefer answering in Chinese when the user speaks Chinese."
            ),
        }
    ]
    messages.extend(message.model_dump() for message in request.messages)

    payload = {
        "model": settings.ollama_model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.7},
    }

    try:
        async with httpx.AsyncClient(timeout=120, trust_env=False) as client:
            response = await client.post(
                f"{settings.ollama_base_url.rstrip('/')}/api/chat",
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text
        raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Failed to connect to Ollama. Make sure Ollama is running and "
                f"reachable at {settings.ollama_base_url}."
            ),
        ) from exc

    data = response.json()
    try:
        reply = data["message"]["content"]
    except (KeyError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="Ollama returned an unexpected response.") from exc

    return ChatResponse(reply=reply.strip())
