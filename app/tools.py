import aioredis


class RedisTools:

    def __init__(self):
        self.redis = None

    async def setup(self):
        self.redis = await aioredis.from_url('redis://redis')

    async def get_key(self, key: str) -> str:
        return await self.redis.get(key)

    async def set_key(self, key: str, value: str, expire_time: int):
        if expire_time:
            await self.redis.setex(key, expire_time, value)
        else:
            await self.redis.set(key, value)

    async def delete_key(self, key: str):
        await self.redis.delete(key)

    async def get_list(self, key: str) -> list:
        return await self.redis.lrange(key, 0, -1)

    async def add_to_list(self, key: str, value: str, expire_time: int):
        await self.redis.rpush(key, value)
        if expire_time:
            await self.redis.expire(key, expire_time)

    async def invalidate_cache_key(self, key: str):
        await self.delete_key(key)

    async def clear_all(self):
        await self.redis.flushall()


redis_client = RedisTools()
