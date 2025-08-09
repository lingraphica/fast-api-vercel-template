from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from typing import Any
from api.helpers.auth import get_api_key
from api.helpers.phrase_building import PhraseBuildingRequest, build_phrase_from_items
from api.helpers.status_map import STATUS_MAP
from api.helpers.provider_model import is_valid_provider_model
from dotenv import load_dotenv
from api.utils.logger import configure_logger

load_dotenv()
logger = configure_logger(__name__)

router = APIRouter(dependencies=[Depends(get_api_key)])


@router.post("/api/phrase-building", response_model=Any)
async def phrase_building(req: PhraseBuildingRequest):
    # logger.info(f"Received request: {req}")
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Content-Type, x-api-key",
    }
    if not req.items or not isinstance(req.items, list) or len(req.items) == 0:
        logger.warning("Validation failed: missing or invalid items field")
        return ORJSONResponse(
            status_code=STATUS_MAP["BAD_REQUEST"]["status_code"],
            content={"error": STATUS_MAP["BAD_REQUEST"]["message"]},
            headers=headers,
        )
    selected_provider = "bedrock"
    selected_model = "us.meta.llama3-2-11b-instruct-v1:0"
    if is_valid_provider_model(req.provider, req.model):
        selected_provider = req.provider
        selected_model = req.model
    try:
        result = await build_phrase_from_items(
            req.items,
            req.previousAttempts,
            selected_model,
            selected_provider,
            req.temperature,
            req.max_tokens,
            req.top_p,
        )
        # logger.info(f"Phrase building result: {result}")
        data = {
            "message": result["message"],
            "model": selected_model,
            "prompt_version": result["prompt_version"],
            "usage": result["usage"],
        }
        return ORJSONResponse(
            status_code=STATUS_MAP["SUCCESS"]["status_code"],
            content={"data": data},
            headers=headers,
        )
    except Exception as error:
        logger.error(f"Error in phrase_building: {error}", exc_info=True)
        return ORJSONResponse(
            status_code=STATUS_MAP["INTERNAL_SERVER_ERROR"]["status_code"],
            content={"error": STATUS_MAP["INTERNAL_SERVER_ERROR"]["message"]},
            headers=headers,
        )
