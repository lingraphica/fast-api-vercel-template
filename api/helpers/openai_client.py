import httpx
from api.helpers.provider_model import get_api_key, get_endpoint
from typing import Any, Dict
from api.utils.logger import configure_logger

logger = configure_logger(__name__)

function_schema = {
    "name": "generate_suggestions",
    "description": "Generates communication responses with text and emoji version",
    "parameters": {
        "type": "object",
        "properties": {
            "suggestions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "text": {"type": "string"},
                        "emoji": {"type": "string"},
                    },
                    "required": ["id", "text", "emoji"],
                },
            },
        },
        "required": ["suggestions"],
    },
}


async def get_text_suggestion(
    prompt: str,
    model: str,
    provider: str = "openai",
    system_prompt: str = "",
    temperature: float = 0.2,
    max_tokens: int = 500,
    top_p: float = 0.8,
) -> Dict[str, Any]:
    logger.info(
        f"get_text_suggestion called with model={model}, provider={provider}, prompt={prompt}"
    )
    api_key = get_api_key(provider)
    endpoint = get_endpoint(provider)
    if not api_key:
        logger.error("OPEN_AI_API_KEY is not set (or model-specific key missing)")
        raise RuntimeError("OPEN_AI_API_KEY is not set (or model-specific key missing)")
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "stream": False,
        "functions": [function_schema],
        "function_call": {"name": "generate_suggestions"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint, json=body, headers=headers)
            data = response.json()
        if not response.status_code == 200:
            message = data.get("error", {}).get("message", "OpenAI API error")
            logger.error(f"OpenAI API error: {message}")
            raise RuntimeError(message)
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("function_call", {})
            .get("arguments", "")
        )
        usage = {
            "prompt_tokens": data.get("usage", {}).get("prompt_tokens", 0),
            "completion_tokens": data.get("usage", {}).get("completion_tokens", 0),
            "total_tokens": data.get("usage", {}).get("total_tokens", 0),
        }
        result = {"content": content or "", "usage": usage or {}}
        logger.info(f"get_text_suggestion output: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in get_text_suggestion: {e}", exc_info=True)
        raise
