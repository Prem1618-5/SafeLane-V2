import logging
import httpx
from platform_app.server.services.db import (
    get_registration_by_id, update_registration_sync,
    save_pr_record, save_activity_event,
)
from platform_app.server.services.auth_service import decrypt_token

logger = logging.getLogger('safelane.platform')

GITHUB_API_BASE = "https://api.github.com"


async def sync_repository(registration_id: int):
    """Synchronize a connected repository's pull requests and activity."""
    reg = await get_registration_by_id(registration_id)
    if not reg or not reg.is_active:
        logger.warning(f"Registration {registration_id} not found or inactive")
        return

    try:
        token = decrypt_token(reg.encrypted_token)
    except Exception as e:
        await update_registration_sync(registration_id, error=f"Token decryption failed: {e}")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "SafeLane",
    }

    try:
        async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
            # Sync recent pull requests
            pr_resp = await client.get(
                f"{GITHUB_API_BASE}/repos/{reg.owner}/{reg.repo}/pulls",
                params={"state": "all", "per_page": 20, "sort": "updated", "direction": "desc"},
            )
            if pr_resp.status_code == 200:
                for pr in pr_resp.json():
                    await save_pr_record(
                        registration_id=registration_id,
                        pr_number=pr["number"],
                        title=pr.get("title"),
                        state=pr.get("state"),
                        head_sha=pr.get("head", {}).get("sha"),
                        author=pr.get("user", {}).get("login"),
                    )

            # Log sync activity
            await save_activity_event(
                registration_id=registration_id,
                event_type="sync_completed",
                payload={"prs_synced": len(pr_resp.json()) if pr_resp.status_code == 200 else 0},
            )

        await update_registration_sync(registration_id, error=None)
        logger.info(f"Successfully synced {reg.owner}/{reg.repo}")

    except Exception as e:
        error_msg = f"Sync failed: {type(e).__name__}: {e}"
        logger.error(f"Sync failed for {reg.owner}/{reg.repo}: {e}")
        await update_registration_sync(registration_id, error=error_msg)
