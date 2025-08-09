import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

PROVIDER_MODEL_MAP: Dict[str, Dict[str, Any]] = {
    "openai": {
        "models": ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano"],
        "api_key": os.environ.get("OPEN_AI_API_KEY", "mocked-open-ai-api-key"),
        "endpoint": os.environ.get(
            "OPEN_AI_ENDPOINT", "https://api.openai.com/v1/chat/completions"
        ),
    },
    "cerebras": {
        "models": ["llama-4-scout-17b-16e-instruct", "llama3.1-8b"],
        "api_key": os.environ.get("CEREBRAS_API_KEY", "mocked-cerebras-api-key"),
        "endpoint": os.environ.get(
            "CEREBRAS_ENDPOINT", "https://api.cerebras.ai/v1/chat/completions"
        ),
    },
    "bedrock": {
        "models": [
            "amazon.nova-lite-v1:0",
            "us.meta.llama3-2-3b-instruct-v1:0",
            "us.meta.llama3-2-11b-instruct-v1:0",
        ],
        "api_key": os.environ.get("BEDROCK_API_KEY", "mocked-bedrock-api-key"),
        "endpoint": "",
    },
    "sagemaker": {
        "models": ["llama-3b"],
        "api_key": "",
        "endpoint": "",
    },
}


def is_valid_provider_model(
    provider: str, model: str, provider_map: Dict[str, Any] = PROVIDER_MODEL_MAP
) -> bool:
    if not provider or not model:
        return False
    provider_entry = provider_map.get(provider)
    if not provider_entry or not isinstance(provider_entry.get("models"), list):
        return False
    return model in provider_entry["models"]


def get_api_key(
    provider: str = "openai", provider_map: Dict[str, Any] = PROVIDER_MODEL_MAP
) -> str:
    return provider_map[provider]["api_key"]


def get_endpoint(
    provider: str = "openai", provider_map: Dict[str, Any] = PROVIDER_MODEL_MAP
) -> str:
    return provider_map[provider]["endpoint"]
