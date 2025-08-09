from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from utils.auth import get_api_key
from models.model import ModelRead

router = APIRouter(
    prefix="/api/model", tags=["model"], dependencies=[Depends(get_api_key)]
)


@router.get("/", response_model=List[ModelRead])
async def get_models():
    """Get all models"""
    try:
        return [
            ModelRead(
                id=uuid.uuid4(),
                name="Model 1",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch models: {str(e)}",
        )
