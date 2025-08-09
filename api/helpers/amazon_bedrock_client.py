import boto3
from typing import Any, Dict

from utils.logger import configure_logger

logger = configure_logger(__name__)


async def get_bedrock_text_suggestion(
    prompt: str,
    selected_model: str,
    system_prompt: str = "",
    temperature: float = 0.2,
    max_tokens: int = 500,
    top_p: float = 0.8,
) -> Dict[str, Any]:
    logger.info(
        f"get_bedrock_text_suggestion called with model={selected_model}, prompt={prompt}"
    )
    import asyncio

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None,
            _sync_bedrock_call,
            prompt,
            selected_model,
            system_prompt,
            temperature,
            max_tokens,
            top_p,
        )
        logger.info(f"get_bedrock_text_suggestion output: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in get_bedrock_text_suggestion: {e}", exc_info=True)
        raise


def _sync_bedrock_call(
    prompt, selected_model, system_prompt, temperature, max_tokens, top_p
):
    logger.info(
        f"_sync_bedrock_call called with model={selected_model}, prompt={prompt}"
    )
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    request = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"text": f"{system_prompt}\n\n{prompt}"},
                ],
            },
        ],
        "modelId": selected_model,
        "inferenceConfig": {
            "maxTokens": max_tokens,
            "temperature": temperature,
            "topP": top_p,
        },
    }
    try:
        response = client.converse(**request)
        usage = {
            "prompt_tokens": response.get("usage", {}).get("inputTokens", 0),
            "completion_tokens": response.get("usage", {}).get("outputTokens", 0),
            "total_tokens": response.get("usage", {}).get("totalTokens", 0),
        }
        top_response = response["output"]["message"]["content"][0]["text"]
        result = {"content": top_response or "", "usage": usage or {}}
        logger.info(f"_sync_bedrock_call output: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in _sync_bedrock_call: {e}", exc_info=True)
        raise
