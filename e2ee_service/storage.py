import logging
from uuid import UUID

from redis.asyncio import Redis

from .constants import TTL_30_DAYS
from .schemas import KeyBundle, UserKeys, DeviceKeys
from .utils import build_redis_device_key, build_redis_devices_key, build_redis_otpk_key

logger = logging.getLogger(__name__)


async def add_key_bundle(
        redis: Redis,
        user_id: UUID,
        device_id: str,
        key_bundle: KeyBundle
) -> bool:
    async with redis.pipeline(transaction=True) as pipe:
        redis_device_key = build_redis_devices_key(user_id, device_id)
        await pipe.hset(
            redis_device_key, mapping=key_bundle.model_dump(exclude={"one_time_pre_keys"})
        )
        await pipe.expire(redis_device_key, TTL_30_DAYS)
        if key_bundle.one_time_pre_keys:
            redis_otpk_key = build_redis_otpk_key(user_id, device_id)
            await pipe.delete(redis_otpk_key)
            await pipe.rpush(redis_otpk_key, *key_bundle.one_time_pre_keys)
            await pipe.expire(redis_otpk_key, TTL_30_DAYS)
        redis_devices_key = build_redis_devices_key(user_id)
        await pipe.sadd(redis_devices_key, device_id)
        await pipe.expire(redis_devices_key, TTL_30_DAYS)
        await pipe.execute()
    logger.info("Keys stored for user %s, device %s", user_id, device_id)
    return True


async def get_device_keys(redis: Redis, user_id: UUID, device_id: str) -> DeviceKeys:
    redis_device_key = build_redis_device_key(user_id, device_id)
    data = await redis.hgetall(redis_device_key)
    return DeviceKeys.model_validate(data)


async def get_user_keys(redis: Redis, user_id: UUID) -> list[UserKeys]:
    redis_devices_key = build_redis_devices_key(user_id)
    device_ids = [
        device_id.decode("utf-8") for device_id in redis.smembers(redis_devices_key)
    ]
    devices_keys: list[DeviceKeys] = []
    for device_id in device_ids:
        device_keys = await get_device_keys(redis, user_id, device_id)
        if device_keys:
            ...
