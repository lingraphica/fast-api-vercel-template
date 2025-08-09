from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from api.helpers.format_util import strip_markdown_code_fences
import orjson
from api.utils.logger import configure_logger

logger = configure_logger(__name__)

router = APIRouter()


class Suggestion(BaseModel):
    id: Any
    text: str
    emoji: Optional[str] = None


class GenerateSuggestionsRequest(BaseModel):
    text: str = Field(..., min_length=1)  # Minimum of 1 character
    objective: str = Field(..., min_length=1)  # Minimum of 1 character
    num_replies: int = Field(..., ge=1)  # Minimum of 1 reply
    model: Optional[str] = None
    mood: Optional[str] = None
    complexity: Optional[int] = Field(..., ge=1, le=3)  # Minimum of 1, maximum of 3
    previous_suggestions: Optional[List[str]] = None
    context: Optional[List[str]] = None
    provider: Optional[str] = None
    temperature: Optional[float] = Field(..., ge=0, le=1)  # Minimum of 0, maximum of 1
    max_tokens: Optional[int] = Field(..., ge=1)  # Minimum of 1 token
    top_p: Optional[float] = Field(..., ge=0, le=1)  # Minimum of 0, maximum of 1
    num_emojis: Optional[int] = Field(..., ge=0)  # Minimum of 0 emojis


class GenerateSuggestionsResponse(BaseModel):
    text: str
    model: str
    prompt_version: str
    suggestions: List[Suggestion]
    usage: dict


def create_response(input_text, reply, model):
    logger.info(f"create_response called with input_text={input_text}, model={model}")
    clean_reply = strip_markdown_code_fences(reply["content"])
    parsed_reply = None
    try:
        parsed_reply = orjson.loads(clean_reply)
    except Exception as e:
        logger.error(f"Failed to parse model response JSON: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to parse model response JSON."
        )
    suggestions = [
        Suggestion(id=phrase["id"], text=phrase["text"], emoji=phrase.get("emoji"))
        for phrase in parsed_reply["suggestions"]
    ]
    response = GenerateSuggestionsResponse(
        text=input_text,
        model=model,
        prompt_version="v1",
        suggestions=suggestions,
        usage=reply["usage"],
    )
    logger.info(f"create_response output: {response}")
    return response
