from fastapi import HTTPException, status, Security
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv

load_dotenv()

# API Key and Authentication
header_scheme = APIKeyHeader(name="x-api-key")
api_key = os.getenv("X_API_KEY")


# TODO: This still returns 403 Forbidden right now on failure
def get_api_key(api_key_header: str = Security(header_scheme)):
    # raise Exception(api_key)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="X_API_KEY is not set",
        )
    if api_key_header == api_key:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
