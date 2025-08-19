import litellm
from api.helpers.provider_model import get_api_key, get_endpoint
from litellm.caching.caching import Cache
from typing import Any, Dict
from api.utils.logger import configure_logger

# from litellm import acompletion, success_callback
import os
from dotenv import load_dotenv

litellm.cache = Cache()
load_dotenv()

logger = configure_logger(__name__)

function_schema_generate_suggestions = {
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

# TODO function schema for phrase building


# track_cost_callback
def track_cost_callback(
    kwargs,  # kwargs to completion
    completion_response,  # response from completion
    start_time,
    end_time,  # start/end time
):
    try:
        response_cost = kwargs.get("response_cost", 0)
        logger.info(f"streaming response_cost: {response_cost}")
    except Exception as e:
        logger.error(f"Error in track_cost_callback: {e}", exc_info=True)
        pass


# set callback
litellm.success_callback = [track_cost_callback]  # set custom callback function


async def get_text_suggestion(
    prompt: str,
    model: str,
    provider: str = "openai",
    system_prompt: str = "",
    messages: list = [],
    temperature: float = 0.2,
    max_tokens: int = 500,
    top_p: float = 0.8,
    function_schema: dict = None,
) -> Dict[str, Any]:
    # logger.info(
    #     f"get_text_suggestion called with model={model}, provider={provider}, prompt={prompt}"
    # )

    if provider == "bedrock":
        os.environ["AWS_ACCESS_KEY_ID"] = os.environ.get(
            "AWS_ACCESS_KEY_ID", "mocked-aws-access-key-id"
        )
        os.environ["AWS_SECRET_ACCESS_KEY"] = os.environ.get(
            "AWS_SECRET_ACCESS_KEY", "mocked-aws-secret-access-key"
        )
    else:
        litellm.api_key = get_api_key(provider)
        litellm.api_base = get_endpoint(provider)
        if not get_api_key(provider):
            # TODO adjust-this to litellm
            logger.error(
                f"{provider} API key is not set (or model-specific key missing)"
            )
            raise RuntimeError(
                f"{provider} API key is not set (or model-specific key missing)"
            )
    if not messages or len(messages) <= 0:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
    try:
        response = await litellm.acompletion(
            model=f"{provider}/{model}",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            functions=[function_schema] if function_schema else None,
            function_call={"name": function_schema["name"]}
            if function_schema
            else None,
            stream=False,
        )
        content = response["choices"][0]["message"]["content"]
        cost = (
            response._hidden_params["response_cost"]
            if "response_cost" in response._hidden_params
            else 0
        )
        usage = {
            "prompt_tokens": response["usage"]["prompt_tokens"],
            "completion_tokens": response["usage"]["completion_tokens"],
            "total_tokens": response["usage"]["total_tokens"],
            "cost": cost,
        }
        print(response._hidden_params)
        result = {"content": content or "", "usage": usage or {}}
        # logger.info(f"get_text_suggestion output: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in get_text_suggestion: {e}", exc_info=True)
        raise
