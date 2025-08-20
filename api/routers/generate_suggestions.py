from fastapi import APIRouter, Depends, Body
from fastapi.responses import ORJSONResponse
from typing import Any
from api.helpers.generate_suggestions import GenerateSuggestionsRequest, create_response
from api.helpers.status_map import STATUS_MAP
from api.helpers.provider_model import is_valid_provider_model
from api.helpers.prompt_generation import create_prompt
from api.helpers.openai_client import get_text_suggestion
from api.helpers.amazon_bedrock_client import get_bedrock_text_suggestion
from api.helpers.auth import get_api_key
from api.utils.logger import configure_logger

logger = configure_logger(__name__)

router = APIRouter(dependencies=[Depends(get_api_key)])


@router.post("/api/generate-suggestions", response_model=Any)
async def generate_suggestions(
    req: GenerateSuggestionsRequest = Body(
        default={
            "text": "Do you want to watch stay inside and watch a movie, or go for a walk?",
            "objective": "affirm",
            "num_replies": 1,
            "mode": "",
            "mood": "Neutral",
            "previousAttempts": [],
            "provider": "bedrock",
            "context": [],
            "model": "amazon.nova-lite-v1:0",
            "temperature": 0.7,
        }
    ),
):
    logger.info(f"Received request: {req}")
    # CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Content-Type, x-api-key",
    }
    # Validate required fields
    if not req.text or not req.objective or not req.num_replies:
        logger.warning("Validation failed: missing required fields")
        return ORJSONResponse(
            status_code=STATUS_MAP["BAD_REQUEST"]["status_code"],
            content={"error": STATUS_MAP["BAD_REQUEST"]["message"]},
            headers=headers,
        )
    # Provider/model selection
    selected_provider = req.provider or "bedrock"
    selected_model = req.model or "us.meta.llama3-2-11b-instruct-v1:0"
    if is_valid_provider_model(selected_provider, selected_model):
        selected_provider = selected_provider
        selected_model = selected_model
    selected_num_emojis = req.num_emojis or 0
    selected_mood = req.mood or "Neutral"
    system_prompt = (
        "You are a communication assistant for people with language difficulties. \n"
        "For every phrase, generate:\n"
        "- a plain text version\n"
    )
    if selected_num_emojis > 0:
        system_prompt += f"- an emoji version with at least {selected_num_emojis} relevant emojis per response (e.g., facial expressions, objects, actions)."
    prompt = create_prompt(
        req.text,
        req.objective,
        req.num_replies,
        selected_mood,
        req.complexity or 1,
        req.previousAttempts or [],
        req.context or [],
        selected_num_emojis,
    )
    try:
        if selected_provider == "bedrock":
            reply = await get_bedrock_text_suggestion(
                prompt,
                selected_model,
                system_prompt,
                req.temperature or 0.7,
                req.max_tokens or 500,
                req.top_p or 0.8,
            )
        else:
            reply = await get_text_suggestion(
                prompt,
                selected_model,
                selected_provider,
                system_prompt,
                req.temperature or 0.7,
                req.max_tokens or 500,
                req.top_p or 0.8,
            )
        logger.info(f"Model reply: {reply}")
        data = create_response(req.text, reply, selected_model)
        return ORJSONResponse(
            status_code=STATUS_MAP["SUCCESS"]["status_code"],
            content={"data": data.model_dump()},
            headers=headers,
        )
    except Exception as error:
        logger.error(f"Error in generate_suggestions: {error}", exc_info=True)
        return ORJSONResponse(
            status_code=STATUS_MAP["INTERNAL_SERVER_ERROR"]["status_code"],
            content={"error": STATUS_MAP["INTERNAL_SERVER_ERROR"]["message"]},
            headers=headers,
        )
