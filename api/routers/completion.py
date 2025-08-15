from fastapi import APIRouter, Depends, Body
from fastapi.responses import ORJSONResponse
from typing import Any
from api.helpers.status_map import STATUS_MAP
from api.helpers.provider_model import is_valid_provider_model
from api.helpers.openai_client import get_text_suggestion
from api.helpers.amazon_bedrock_client import get_bedrock_text_suggestion
from api.helpers.auth import get_api_key
from api.utils.logger import configure_logger
from pydantic import BaseModel

logger = configure_logger(__name__)

router = APIRouter(dependencies=[Depends(get_api_key)])


class CompletionRequest(BaseModel):
    prompt: str
    model: str = "us.meta.llama3-2-11b-instruct-v1:0"
    provider: str = "bedrock"
    system_prompt: str = "You are a helpful assistant."
    temperature: float = 0.7
    max_tokens: int = 500
    top_p: float = 0.8


class CompletionResponse(BaseModel):
    text: str
    model: str
    provider: str


@router.post("/api/completion", response_model=Any)
async def completion(
    req: CompletionRequest = Body(
        default={
            "prompt": "Hello, how are you?",
            "model": "us.meta.llama3-2-11b-instruct-v1:0",
            "provider": "bedrock",
            "system_prompt": "You are a helpful assistant.",
            "temperature": 0.7,
            "max_tokens": 500,
            "top_p": 0.8,
        }
    ),
):
    logger.info(f"Received completion request: {req}")
    # CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Content-Type, x-api-key",
    }

    # Validate required fields
    if not req.prompt:
        logger.warning("Validation failed: missing prompt")
        return ORJSONResponse(
            status_code=STATUS_MAP["BAD_REQUEST"]["status_code"],
            content={"error": STATUS_MAP["BAD_REQUEST"]["message"]},
            headers=headers,
        )

    # Provider/model selection
    selected_provider = "bedrock"
    selected_model = "us.meta.llama3-2-11b-instruct-v1:0"
    if is_valid_provider_model(req.provider, req.model):
        selected_provider = req.provider
        selected_model = req.model

    try:
        if selected_provider == "bedrock":
            reply = await get_bedrock_text_suggestion(
                req.prompt,
                selected_model,
                req.system_prompt,
                req.temperature,
                req.max_tokens,
                req.top_p,
            )
        else:
            reply = await get_text_suggestion(
                req.prompt,
                selected_model,
                selected_provider,
                req.system_prompt,
                req.temperature,
                req.max_tokens,
                req.top_p,
            )

        logger.info(f"Model reply: {reply}")

        response_data = CompletionResponse(
            text=reply, model=selected_model, provider=selected_provider
        )

        return ORJSONResponse(
            status_code=STATUS_MAP["SUCCESS"]["status_code"],
            content={"data": response_data.model_dump()},
            headers=headers,
        )
    except Exception as error:
        logger.error(f"Error in completion: {error}", exc_info=True)
        return ORJSONResponse(
            status_code=STATUS_MAP["INTERNAL_SERVER_ERROR"]["status_code"],
            content={"error": STATUS_MAP["INTERNAL_SERVER_ERROR"]["message"]},
            headers=headers,
        )
