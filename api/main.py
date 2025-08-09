from typing import Union
import httpx
import uvloop
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from utils.logger import configure_logger
from routers.model import router as model_router

logger = configure_logger(__name__)

# Install uvloop as the event loop policy
uvloop.install()


tags_metadata = [
    {
        "name": "default",
        "description": "Default endpoint",
    }
]

app = FastAPI(
    title="FastAPI Vercel Template",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    openapi_tags=tags_metadata,
)


@app.on_event("startup")
async def startup_event():
    """Start the job processor when the app starts."""
    logger.info("Starting FastAPI Vercel Template")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the job processor when the app shuts down."""
    logger.info("Shutting down FastAPI Vercel Template")


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/test")
async def test():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com")
        return response.json()


app.include_router(model_router)
