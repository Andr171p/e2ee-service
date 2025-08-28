import base64
import time
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


def current_timestamp() -> int:
    """Получает текущее время в формате timestamp."""
    return int(time.time())


class KeyType(StrEnum):
    IDENTITY = "identity"          # Долгосрочный идентификационный ключ
    SIGNED_PRE = "signed_pre"      # Среднесрочный подписанный ключ
    ONE_TIME_PRE = "one_time_pre"  # Одноразовые ключи (буфер)


class KeyBundle(BaseModel):
    """Связка ключей клиента (храниться на сервере)

    Attributes:
        identity_key: Публичный ключ в формате base64.
        signed_pre_key: Предварительно подписанный ключ.
        signed_pre_key_signature: Подпись предварительно подписанного ключа.
        one_time_pre_keys: Одноразовые ключи клиента.
    """
    identity_key: str
    signed_pre_key: str
    signed_pre_key_signature: str
    one_time_pre_keys: list[str] = Field(default_factory=list)

    @field_validator("identity_key", "signed_pre_key", "signed_pre_key_signature")
    def validate_base64(cls, value: str) -> str:
        try:
            base64.b64decode(value, validate=True)
            return value
        except ValueError:
            raise ValueError("Invalid base64 encoding")

    @field_validator("one_time_pre_keys")
    def validate_one_time_pre_keys(cls, one_time_pre_keys: list[str]) -> list[str]:
        try:
            for one_time_pre_key in one_time_pre_keys:
                base64.b64decode(one_time_pre_key, validate=True)
        except ValueError:
            raise ValueError("Invalid base64 encoding for one-time pre keys")
        else:
            return one_time_pre_keys


class DeviceKeyBundle(BaseModel):
    """Представление ключей одного устройства для ответа клиенту.
    Возвращается, когда другой пользователь запрашивает ключи для установления сессии.

    Attributes:
        device_id: Идентификатор устройства (телефон, ноутбук и.т.д).
        identity_key: Публичный идентификационный ключ.
        signed_pre_key: Подписанный промежуточный ключ.
        signed_pre_key_signature: Подпись для верификации.
        one_time_pre_key: Один неиспользованный одноразовый ключ (извлекается из пула).
    """
    device_id: str
    identity_key: str
    signed_pre_key: str
    signed_pre_key_signature: str
    one_time_pre_key: str | None = None
    key_timestamp: int = Field(default_factory=current_timestamp)


class UserDevices(BaseModel):
    """Полный пакет ключей всех устройств пользователя."""
    user_id: UUID
    devices: list[DeviceKeyBundle]
