from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from helpers.format_util import strip_markdown_code_fences
from helpers.prompt_generation import create_phrase_building_prompt
from helpers.litellm_client import get_text_suggestion
import orjson
from utils.logger import configure_logger

logger = configure_logger(__name__)

router = APIRouter()


class PhraseBuildingRequest(BaseModel):
    items: List[str] = Field(..., min_items=1)  # Minimum of 1 item
    previousAttempts: Optional[List[str]] = []
    model: Optional[str] = None
    provider: Optional[str] = None
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 500
    top_p: Optional[float] = 0.8

    class Config:
        json_schema_extra = {
            "example": {
                "items": ["coffee", "cream"],
                "previousAttempts": [],
                "model": "us.meta.llama3-2-11b-instruct-v1:0",
                "provider": "bedrock",
                "temperature": 0.9,
                "max_tokens": 500,
                "top_p": 0.8,
            }
        }


class PhraseBuildingResponse(BaseModel):
    message: str
    model: str
    prompt_version: str
    usage: dict


def create_response(reply: str) -> str:
    # logger.info(f"create_response called with reply={reply}")
    clean_reply = strip_markdown_code_fences(reply)
    try:
        parsed_reply = orjson.loads(clean_reply)
    except Exception as e:
        logger.error(f"Failed to parse model response JSON: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to parse model response JSON."
        )
    result = parsed_reply["suggestions"][0]["text"]
    # logger.info(f"create_response output: {result}")
    return result


async def build_phrase_from_items(
    items: List[str],
    previous_attempts: Optional[List[str]],
    model: str,
    provider: str,
    temperature: float,
    max_tokens: int,
    top_p: float,
) -> dict:
    # logger.info(
    #     f"build_phrase_from_items called with items={items}, model={model}, provider={provider}"
    # )
    prompt = create_phrase_building_prompt(items, previous_attempts)
    try:
        data = await get_text_suggestion(
            prompt, model, provider, "", temperature, max_tokens, top_p
        )
        message = create_response(data["content"])
        result = {
            "message": message,
            "model": model,
            "usage": data["usage"],
            "prompt_version": "phrase-v1",
        }
        # logger.info(f"build_phrase_from_items output: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in build_phrase_from_items: {e}", exc_info=True)
        raise
