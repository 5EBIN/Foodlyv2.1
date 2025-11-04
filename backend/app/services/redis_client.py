import aioredis
import json
from app.core.config import settings

_redis = None

async def get_redis():
    global _redis
    if _redis is None:
        _redis = await aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    return _redis

# helpers
async def cache_set(key: str, value, ex: int = 300):
    r = await get_redis()
    await r.set(key, json.dumps(value), ex=ex)

async def cache_get(key: str):
    r = await get_redis()
    v = await r.get(key)
    if v is None:
        return None
    return json.loads(v)
