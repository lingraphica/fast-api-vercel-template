from fastapi import APIRouter, Depends, Body
from fastapi.responses import ORJSONResponse
from typing import Any, Optional
from api.helpers.status_map import STATUS_MAP
from api.helpers.provider_model import is_valid_provider_model
from api.helpers.litellm_client import get_text_suggestion
from api.helpers.auth import get_api_key
from api.utils.logger import configure_logger
from pydantic import BaseModel, field_validator, model_validator

logger = configure_logger(__name__)

router = APIRouter(dependencies=[Depends(get_api_key)])


class CompletionRequest(BaseModel):
    prompt: Optional[str] = None
    model: str = "us.meta.llama3-2-11b-instruct-v1:0"
    provider: str = "bedrock"
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 500
    top_p: float = 0.8
    messages: list = []  # optional

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v

    @field_validator("system_prompt")
    @classmethod
    def validate_system_prompt(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v

    @model_validator(mode="after")
    def validate_at_least_one_input(self):
        has_prompt = self.prompt is not None and self.prompt.strip() != ""
        has_system_prompt = (
            self.system_prompt is not None and self.system_prompt.strip() != ""
        )
        has_messages = len(self.messages) > 0

        if not (has_prompt or has_system_prompt or has_messages):
            raise ValueError(
                "At least one of 'prompt', 'system_prompt', or 'messages' must be provided"
            )

        return self


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
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"},
            ],
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

    # Provider/model selection
    selected_provider = "bedrock"
    selected_model = "amazon.nova-lite-v1:0"
    if is_valid_provider_model(req.provider, req.model):
        selected_provider = req.provider
        selected_model = req.model

    try:
        # Use litellm client for all providers
        result = await get_text_suggestion(
            prompt=req.prompt,
            model=selected_model,
            provider=selected_provider,
            system_prompt=req.system_prompt,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            top_p=req.top_p,
            messages=req.messages,
        )

        logger.info(f"Model reply: {result}")

        response_data = CompletionResponse(
            text=result["content"], model=selected_model, provider=selected_provider
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
