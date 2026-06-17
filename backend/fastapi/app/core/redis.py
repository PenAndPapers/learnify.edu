from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis import asyncio as aioredis

from .config import get_cache_url


# 1. Define the lifespan context manager
@asynccontextmanager
async def redis_lifespan(app: FastAPI):
  # This runs on startup
  app.state.redis = aioredis.from_url(
    get_cache_url(),
    encoding="utf-8",
    decode_responses=True,
  )

  yield  # The app runs while this is suspended

  # This runs on shutdown
  await app.state.redis.close()
