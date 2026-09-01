import logging
import httpx
from platform_app.server.services.db import (
    get_registration_by_id, update_registration_sync,
    save_pr_record, save_activity_event, save_analysis_record
)
from platform_app.server.services.auth_service import decrypt_token
from safelane.contracts import PRPayload, RepoContext
from safelane.fabric.controller import orchestrate
import asyncio

logger = logging.getLogger('safelane.platform')

GITHUB_API_BASE = "https://api.github.com"

async def bootstrap_repository(registration_id: int):
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
    
    repo_context = RepoContext(
        registration_id=str(reg.id),
        owner=reg.owner,
        repo=reg.repo,
        gh_token=token,
        azure_search_endpoint=reg.azure_search_endpoint,
        azure_search_key=reg.azure_search_key,
        azure_tenant_id=reg.azure_tenant_id,
        azure_workspace_id=reg.azure_workspace_id,
    )

    try:
        async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
            pr_resp = await client.get(
                f"{GITHUB_API_BASE}/repos/{reg.owner}/{reg.repo}/pulls",
                params={"state": "all", "per_page": 10, "sort": "updated", "direction": "desc"},
            )
            
            prs_synced = 0
            if pr_resp.status_code == 200:
                prs = pr_resp.json()
                for pr in prs:
                    pr_number = pr["number"]
                    head_sha = pr.get("head", {}).get("sha", "")
                    
                    await save_pr_record(
                        registration_id=registration_id,
                        pr_number=pr_number,
                        title=pr.get("title"),
                        state=pr.get("state"),
                        head_sha=head_sha,
                        author=pr.get("user", {}).get("login"),
                    )
                    prs_synced += 1
                    
                    diff_text = ""
                    changed_files = []
                    try:
                        diff_resp = await client.get(
                            f"{GITHUB_API_BASE}/repos/{reg.owner}/{reg.repo}/pulls/{pr_number}",
                            headers={**headers, "Accept": "application/vnd.github.v3.diff"},
                        )
                        if diff_resp.status_code == 200:
                            diff_text = diff_resp.text

                        files_resp = await client.get(
                            f"{GITHUB_API_BASE}/repos/{reg.owner}/{reg.repo}/pulls/{pr_number}/files",
                            headers={**headers, "Accept": "application/vnd.github.v3+json"},
                        )
                        if files_resp.status_code == 200:
                            changed_files = [f["filename"] for f in files_resp.json()]
                            
                        payload = PRPayload(
                            pr_number=pr_number,
                            repo=f"{reg.owner}/{reg.repo}",
                            changed_files=changed_files,
                            diff=diff_text,
                            timestamp=pr.get("updated_at", "1970-01-01T00:00:00Z"),
                            head_sha=head_sha,
                        )
                        report = await orchestrate(payload, repo_context)
                        await save_analysis_record(
                            registration_id=registration_id,
                            pr_number=pr_number,
                            head_sha=head_sha,
                            report=report,
                        )
                    except Exception as analysis_err:
                        logger.error(f"Failed to analyze PR {pr_number} during bootstrap: {analysis_err}")

            await save_activity_event(
                registration_id=registration_id,
                event_type="sync_completed",
                payload={"prs_synced": prs_synced},
            )

        await update_registration_sync(registration_id, error=None)
        logger.info(f"Successfully bootstrapped {reg.owner}/{reg.repo}")

    except Exception as e:
        error_msg = f"Bootstrap failed: {type(e).__name__}: {e}"
        logger.error(f"Bootstrap failed for {reg.owner}/{reg.repo}: {e}")
        await update_registration_sync(registration_id, error=error_msg)

async def sync_repository(registration_id: int):
    await bootstrap_repository(registration_id)
