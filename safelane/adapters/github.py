import os
import hmac
import hashlib
import logging
import json
from typing import Optional

from fastapi import APIRouter, Request, BackgroundTasks, HTTPException, Header
from safelane.contracts import PRPayload, RepoContext
from safelane.fabric.controller import orchestrate
from safelane.fabric.publisher import publish_verdict, publish_commit_verdict

logger = logging.getLogger('safelane.server')

router = APIRouter()


async def get_repo_context(repo: str) -> Optional[RepoContext]:
    """Resolve repository credentials from the database, falling back to env var for local dev."""
    if '/' not in repo:
        return None

    owner, repo_name = repo.split('/', 1)

    # Try database lookup first
    try:
        from platform_app.server.services.db import get_registration
        from platform_app.server.services.auth_service import decrypt_token

        registration = await get_registration(owner, repo_name)
        if registration and registration.is_active:
            token = decrypt_token(registration.encrypted_token)
            custom_holidays = None
            if registration.custom_holiday_dates:
                try:
                    custom_holidays = json.loads(registration.custom_holiday_dates)
                except (json.JSONDecodeError, TypeError):
                    custom_holidays = None

            return RepoContext(
                registration_id=str(registration.id),
                owner=owner,
                repo=repo_name,
                gh_token=token,
                azure_search_endpoint=registration.azure_search_endpoint,
                azure_search_key=registration.azure_search_key,
                azure_tenant_id=registration.azure_tenant_id,
                azure_workspace_id=registration.azure_workspace_id,
                rollback_strategy=registration.rollback_strategy or "branch",
                custom_holiday_dates=custom_holidays,
                deploy_window_start_utc=registration.deploy_window_start_utc,
                deploy_window_end_utc=registration.deploy_window_end_utc,
            )
    except Exception as e:
        logger.warning(f"DB lookup failed for {repo}, falling back to env: {e}")

    # Fallback to env var for local development / testing
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return None
    return RepoContext(
        registration_id="env-fallback",
        owner=owner,
        repo=repo_name,
        gh_token=token,
    )


@router.get("/health")
async def health():
    return {"status": "ok", "service": "safelane"}


async def _run_analysis(payload: PRPayload, repo_context: RepoContext):
    try:
        reg_id = int(repo_context.registration_id) if repo_context.registration_id and repo_context.registration_id.isdigit() else None
        if reg_id and payload.head_sha:
            try:
                from platform_app.server.services.db import get_analysis_by_sha
                existing = await get_analysis_by_sha(reg_id, payload.pr_number, payload.head_sha)
                if existing:
                    logger.debug(f"Skipping analysis for PR #{payload.pr_number} sha={payload.head_sha[:7]} — already analyzed")
                    return
            except Exception as e:
                logger.warning(f"Could not check existing analysis: {e}")

        report = await orchestrate(payload, repo_context)
        await publish_verdict(report, payload.repo, payload.pr_number, repo_context.gh_token)

        # Persist analysis record to DB
        try:
            from platform_app.server.services.db import save_analysis_record
            await save_analysis_record(
                registration_id=reg_id,
                pr_number=payload.pr_number,
                head_sha=payload.head_sha,
                report=report,
            )
        except Exception as db_err:
            logger.warning(f"Failed to save analysis record: {db_err}")

    except Exception as e:
        logger.error(f"Analysis failed: {e}")

async def _run_push_analysis(payload: PRPayload, repo_context: RepoContext):
    try:
        reg_id = int(repo_context.registration_id) if repo_context.registration_id and repo_context.registration_id.isdigit() else None
        if reg_id and payload.head_sha:
            try:
                from platform_app.server.services.db import get_analysis_by_sha
                existing = await get_analysis_by_sha(reg_id, 0, payload.head_sha)
                if existing:
                    logger.debug(f"Skipping push analysis for sha={payload.head_sha[:7]} — already analyzed")
                    return
            except Exception as e:
                logger.warning(f"Could not check existing push analysis: {e}")

        report = await orchestrate(payload, repo_context)
        
        target_url = "" # Can link to safelane dashboard
        await publish_commit_verdict(report, payload.repo, payload.head_sha, repo_context.gh_token, target_url)

        try:
            from platform_app.server.services.db import save_analysis_record
            await save_analysis_record(
                registration_id=reg_id,
                pr_number=0, # Push event
                head_sha=payload.head_sha,
                report=report,
            )
        except Exception as db_err:
            logger.warning(f"Failed to save analysis record for push: {db_err}")

    except Exception as e:
        logger.error(f"Push Analysis failed: {e}")

@router.post("/webhook/pr")
async def webhook_pr(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None),
):
    body = await request.body()
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET")

    if secret:
        if not x_hub_signature_256:
            raise HTTPException(status_code=401, detail="Missing signature")

        expected_mac = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        expected_sig = f"sha256={expected_mac}"
        if not hmac.compare_digest(x_hub_signature_256, expected_sig):
            raise HTTPException(status_code=401, detail="Invalid signature")
    else:
        logger.warning("GITHUB_WEBHOOK_SECRET is not set, bypassing verification. Set it for production use.")

    data = await request.json()

    event = request.headers.get("x-github-event")
    
    if event not in ["pull_request", "push"]:
        return {"status": "ignored", "reason": f"not a supported event: {event}"}
        
    action = data.get("action")
    if event == "pull_request" and action not in ["opened", "synchronize", "reopened"]:
        return {"status": "ignored", "reason": f"action {action} ignored"}
    
    repo_data = data.get("repository", {})
    repo_name = repo_data.get("full_name")
    if not repo_name:
        raise HTTPException(status_code=400, detail="Missing repository full_name")

    repo_context = await get_repo_context(repo_name)
    if not repo_context:
        raise HTTPException(status_code=404, detail="Repo context not found")
        
    if event == "push":
        ref = data.get("ref", "")
        if ref not in ["refs/heads/main", "refs/heads/master"] and ref != f"refs/heads/{repo_data.get('default_branch', 'main')}":
            return {"status": "ignored", "reason": "not default branch push"}
            
        after = data.get("after")
        if not after or after == "0000000000000000000000000000000000000000":
            return {"status": "ignored", "reason": "deleted branch"}
            
        before = data.get("before")
        
        diff_text = ""
        changed_files = []
        try:
            from platform_app.server.services.github_service import get_compare_diff
            diff_text, changed_files = await get_compare_diff(repo_context.gh_token, repo_context.owner, repo_context.repo, before, after)
        except Exception as e:
            logger.error(f"Failed to fetch push diff: {e}")
            
        payload = PRPayload(
            pr_number=0,
            repo=repo_name,
            changed_files=changed_files,
            diff=diff_text,
            timestamp=data.get("head_commit", {}).get("timestamp", "1970-01-01T00:00:00Z"),
            head_sha=after,
            skip_autofix=False,
        )

        background_tasks.add_task(_run_push_analysis, payload, repo_context)
        return {"status": "accepted"}

    pr_data = data.get("pull_request", {})

    # Fetch real PR diff and changed files from GitHub API
    diff_text = ""
    changed_files = []
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {repo_context.gh_token}", "User-Agent": "SafeLane"}
            diff_resp = await client.get(
                f"https://api.github.com/repos/{repo_name}/pulls/{pr_data.get('number', 0)}",
                headers={**headers, "Accept": "application/vnd.github.v3.diff"},
            )
            if diff_resp.status_code == 200:
                diff_text = diff_resp.text

            files_resp = await client.get(
                f"https://api.github.com/repos/{repo_name}/pulls/{pr_data.get('number', 0)}/files",
                headers={**headers, "Accept": "application/vnd.github.v3+json"},
            )
            if files_resp.status_code == 200:
                changed_files = [f["filename"] for f in files_resp.json()]
    except Exception as e:
        logger.error(f"Failed to fetch PR details from GitHub: {e}")

    payload = PRPayload(
        pr_number=pr_data.get("number", 0),
        repo=repo_name,
        changed_files=changed_files,
        diff=diff_text,
        timestamp=pr_data.get("updated_at", "1970-01-01T00:00:00Z"),
        head_sha=pr_data.get("head", {}).get("sha", ""),
        skip_autofix=False,
    )

    background_tasks.add_task(_run_analysis, payload, repo_context)
    return {"status": "accepted"}


@router.post("/analyze")
async def analyze(payload: PRPayload):
    """Synchronous analysis endpoint for testing."""
    repo_context = await get_repo_context(payload.repo)
    report = await orchestrate(payload, repo_context)
    return report
