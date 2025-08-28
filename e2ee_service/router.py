from uuid import UUID

from fastapi import APIRouter, status

from .schemas import KeyBundle

router = APIRouter(prefix="/api/v1/keys", tags=["Keys"])


@router.post(
    path="/{user_id}/{device_id}",
    status_code=status.HTTP_201_CREATED,
    summary="..."
)
async def upload_keys(
        user_id: UUID,
        device_id: str,
        key_bundle: KeyBundle
) -> ...: ...
