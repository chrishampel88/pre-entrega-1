"""Estructuras de datos que valida Pydantic."""

from typing import Literal
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class ModelConfig(BaseModel):
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=200, gt=0)


class ModelResponse(BaseModel):
    provider: str
    content: str
    error: str | None = None
