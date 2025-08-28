from uuid import UUID


def build_redis_device_key(user_id: UUID, device_id: str) -> str:
    return f"keys:user:{user_id}:device:{device_id}"


def build_redis_devices_key(user_id: UUID) -> str:
    return f"devices:user:{user_id}"


def build_redis_otpk_key(user_id: UUID, device_id: str) -> str:
    return f"otpk:user:{user_id}:device:{device_id}"
