import json
import logging
import httpx
from platform_app.server.services.db import (
    get_registration_by_id, update_registration_sync,
    save_pr_record, save_activity_event, save_analysis_record,
    get_analysis_by_sha, set_registration_inactive,
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
    
    custom_holidays = None
    if reg.custom_holiday_dates:
        try:
            custom_holidays = json.loads(reg.custom_holiday_dates) if isinstance(reg.custom_holiday_dates, str) else reg.custom_holiday_dates
        except (json.JSONDecodeError, TypeError):
            custom_holidays = None

    repo_context = RepoContext(
        registration_id=str(reg.id),
        owner=reg.owner,
        repo=reg.repo,
        gh_token=token,
        azure_search_endpoint=reg.azure_search_endpoint,
        azure_search_key=reg.azure_search_key,
        azure_tenant_id=reg.azure_tenant_id,
        azure_workspace_id=reg.azure_workspace_id,
        rollback_strategy=reg.rollback_strategy or "branch",
        custom_holiday_dates=custom_holidays,
        deploy_window_start_utc=reg.deploy_window_start_utc,
        deploy_window_end_utc=reg.deploy_window_end_utc,
    )

    try:
        async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
            pr_resp = await client.get(
                f"{GITHUB_API_BASE}/repos/{reg.owner}/{reg.repo}/pulls",
                params={"state": "all", "per_page": 10, "sort": "updated", "direction": "desc"},
            )
            
            prs_synced = 0
            prs_skipped = 0

            # C3: Handle 404 — repo deleted or access revoked
            if pr_resp.status_code == 404:
                await update_registration_sync(
                    registration_id,
                    error="Repository not found or access revoked on GitHub"
                )
                await set_registration_inactive(registration_id)
                logger.warning(f"Repo {reg.owner}/{reg.repo} returned 404 — marked inactive")
                return

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
                    
                    # C2: Skip analysis if this exact (reg, PR, SHA) was already analyzed
                    if head_sha:
                        existing = await get_analysis_by_sha(registration_id, pr_number, head_sha)
                        if existing:
                            prs_skipped += 1
                            logger.debug(f"Skipping PR #{pr_number} sha={head_sha[:7]} — already analyzed")
                            continue

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
            elif pr_resp.status_code != 409:
                raise Exception(f"GitHub API error fetching PRs: {pr_resp.status_code} {pr_resp.text}")

            await save_activity_event(
                registration_id=registration_id,
                event_type="sync_completed",
                payload={"prs_synced": prs_synced, "prs_skipped": prs_skipped},
            )

            # Analyze latest commits on default branch
            from platform_app.server.services.github_service import get_commit_diff
            commit_resp = await client.get(
                f"{GITHUB_API_BASE}/repos/{reg.owner}/{reg.repo}/commits",
                params={"per_page": 5},
            )

            # C3: Handle 404 on commits endpoint too
            if commit_resp.status_code == 404:
                await update_registration_sync(
                    registration_id,
                    error="Repository not found or access revoked on GitHub"
                )
                await set_registration_inactive(registration_id)
                logger.warning(f"Repo {reg.owner}/{reg.repo} commits returned 404 — marked inactive")
                return

            if commit_resp.status_code == 200:
                commits = commit_resp.json()
                for commit in commits:
                    sha = commit.get("sha")

                    # C2: Skip if this exact commit SHA was already analyzed
                    if sha:
                        existing = await get_analysis_by_sha(registration_id, 0, sha)
                        if existing:
                            logger.debug(f"Skipping commit sha={sha[:7]} — already analyzed")
                            continue

                    diff_text, changed_files = await get_commit_diff(token, reg.owner, reg.repo, sha)
                    if diff_text and changed_files:
                        payload = PRPayload(
                            pr_number=0,
                            repo=f"{reg.owner}/{reg.repo}",
                            changed_files=changed_files,
                            diff=diff_text,
                            timestamp=commit.get("commit", {}).get("author", {}).get("date"),
                            head_sha=sha,
                        )
                        report = await orchestrate(payload, repo_context)
                        await save_analysis_record(
                            registration_id=registration_id,
                            pr_number=0,
                            head_sha=sha,
                            report=report,
                        )
            elif commit_resp.status_code != 409:
                raise Exception(f"GitHub API error fetching commits: {commit_resp.status_code} {commit_resp.text}")

        await update_registration_sync(registration_id, error=None)
        logger.info(f"Successfully bootstrapped {reg.owner}/{reg.repo}")

    except Exception as e:
        error_msg = f"Bootstrap failed: {type(e).__name__}: {e}"
        logger.error(f"Bootstrap failed for {reg.owner}/{reg.repo}: {e}")
        await update_registration_sync(registration_id, error=error_msg)

async def sync_repository(registration_id: int):
    await bootstrap_repository(registration_id)
