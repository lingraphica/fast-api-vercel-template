from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from api.helpers.provider_model import PROVIDER_MODEL_MAP
from api.helpers.status_map import STATUS_MAP
from api.helpers.auth import get_api_key

router = APIRouter(dependencies=[Depends(get_api_key)])


@router.get("/api/models")
def get_models():
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Content-Type, x-api-key",
    }

    models = [
        {
            "provider": provider,
            "models": config["models"],
            "endpoint": config["endpoint"],
        }
        for provider, config in PROVIDER_MODEL_MAP.items()
    ]
    return ORJSONResponse(
        status_code=STATUS_MAP["SUCCESS"]["status_code"],
        content={"data": models},
        headers=headers,
    )
