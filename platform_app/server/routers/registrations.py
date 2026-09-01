from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Annotated
from platform_app.server.routers.auth import get_current_user
from platform_app.server.services.db import (
    create_registration, list_registrations, get_registration_by_id,
    async_session, Registration, get_user_by_github_id,
)
from platform_app.server.services.auth_service import encrypt_token, decrypt_token

router = APIRouter()


class RegistrationCreate(BaseModel):
    owner: str
    repo: str
    azure_search_endpoint: str | None = None
    azure_search_key: str | None = None
    azure_tenant_id: str | None = None
    azure_workspace_id: str | None = None


@router.get("/")
async def get_my_registrations(current_user: Annotated[dict, Depends(get_current_user)]):
    user_id = current_user["github_id"]
    regs = await list_registrations(user_id)
    return [{
        "id": r.id,
        "owner": r.owner,
        "repo": r.repo,
        "is_active": r.is_active,
        "last_synced_at": r.last_synced_at,
        "sync_error": r.sync_error,
        "created_at": r.created_at,
    } for r in regs]


@router.post("/")
async def create_new_registration(req: RegistrationCreate, current_user: Annotated[dict, Depends(get_current_user)]):
    user_id = current_user["github_id"]

    # Get user's encrypted token from DB
    user = await get_user_by_github_id(user_id)
    if not user or not user.encrypted_token:
        raise HTTPException(status_code=401, detail="No GitHub token stored. Please re-authenticate.")

    # Re-encrypt with the user's token for this registration
    token = decrypt_token(user.encrypted_token)
    encrypted = encrypt_token(token)

    reg = await create_registration(
        user_id=user_id,
        owner=req.owner,
        repo=req.repo,
        encrypted_token=encrypted,
        azure_search_endpoint=req.azure_search_endpoint,
        azure_search_key=req.azure_search_key,
        azure_tenant_id=req.azure_tenant_id,
        azure_workspace_id=req.azure_workspace_id,
    )
    return {"id": reg.id, "status": "created"}


from platform_app.server.services import sync_service

@router.post("/{reg_id}/enable")
async def enable_registration(reg_id: int, background_tasks: BackgroundTasks, current_user: Annotated[dict, Depends(get_current_user)]):
    user_id = current_user["github_id"]
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(Registration).where(Registration.id == reg_id, Registration.user_id == user_id)
        )
        reg = result.scalars().first()
        if not reg:
            raise HTTPException(status_code=404, detail="Registration not found")
        reg.is_active = True
        await session.commit()
        
        # Trigger background sync of PRs on connect
        background_tasks.add_task(sync_service.sync_repository, reg_id)
        
        return {"status": "enabled"}


@router.post("/{reg_id}/disable")
async def disable_registration(reg_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    user_id = current_user["github_id"]
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(Registration).where(Registration.id == reg_id, Registration.user_id == user_id)
        )
        reg = result.scalars().first()
        if not reg:
            raise HTTPException(status_code=404, detail="Registration not found")
        reg.is_active = False
        await session.commit()
        return {"status": "disabled"}


@router.delete("/{reg_id}")
async def delete_registration(reg_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    user_id = current_user["github_id"]
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(Registration).where(Registration.id == reg_id, Registration.user_id == user_id)
        )
        reg = result.scalars().first()
        if not reg:
            raise HTTPException(status_code=404, detail="Registration not found")
        reg.is_active = False
        await session.commit()
        return {"status": "deactivated"}
