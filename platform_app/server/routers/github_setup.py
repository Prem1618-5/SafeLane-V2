import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from platform_app.server.routers.auth import get_current_user
from platform_app.server.services.github_service import list_user_repos
from platform_app.server.services.db import get_user_by_github_id
from platform_app.server.services.auth_service import decrypt_token

logger = logging.getLogger('safelane.platform')

router = APIRouter()


async def _get_user_token(current_user: dict) -> str:
    """Retrieve and decrypt the user's GitHub token from the database."""
    user = await get_user_by_github_id(current_user["github_id"])
    if not user or not user.encrypted_token:
        raise HTTPException(status_code=401, detail="No GitHub token stored. Please re-authenticate.")
    return decrypt_token(user.encrypted_token)


@router.get("/user-repos")
async def list_repos(current_user: Annotated[dict, Depends(get_current_user)]):
    """List repositories accessible by the authenticated user."""
    token = await _get_user_token(current_user)
    try:
        repos = await list_user_repos(token)
        return repos
    except ValueError as e:
        msg = str(e).lower()
        if "re-authenticate" in msg or "expired" in msg or "invalid" in msg:
            raise HTTPException(status_code=401, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))

from pydantic import BaseModel
from platform_app.server.services.db import async_session, User
from platform_app.server.services.auth_service import encrypt_token
from platform_app.server.services.github_service import validate_token
from sqlalchemy import select

class TokenRequest(BaseModel):
    token: str

@router.post("/token")
async def update_token(req: TokenRequest, current_user: Annotated[dict, Depends(get_current_user)]):
    """Save or update a GitHub Personal Access Token."""
    try:
        await validate_token(req.token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid GitHub token")

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.github_id == current_user["github_id"])
        )
        db_user = result.scalars().first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db_user.encrypted_token = encrypt_token(req.token)
        await session.commit()

    return {"status": "ok"}
