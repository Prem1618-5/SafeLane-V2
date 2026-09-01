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
        raise HTTPException(status_code=400, detail=str(e))
