import json
import logging
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Annotated
from platform_app.server.routers.auth import get_current_user
from platform_app.server.services.db import (
    list_registrations, get_registration_by_id, get_analysis_records,
    get_analysis_by_pr, get_pr_records,
)
from platform_app.server.services import sync_service
from safelane.contracts import MODULE_WEIGHTS

logger = logging.getLogger('safelane.platform')

router = APIRouter()

@router.post("/repos/{reg_id}/sync")
async def sync_repo(reg_id: int, background_tasks: BackgroundTasks, current_user: Annotated[dict, Depends(get_current_user)]):
    """Manually trigger a sync for a connected repository."""
    user_id = current_user["github_id"]
    reg = await get_registration_by_id(reg_id)
    if not reg or reg.user_id != user_id:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    background_tasks.add_task(sync_service.sync_repository, reg_id)
    return {"status": "sync_triggered", "reg_id": reg_id}

@router.get("/repos")
async def dashboard_repos(current_user: Annotated[dict, Depends(get_current_user)]):
    """List all connected repositories with safety scores and sync status."""
    user_id = current_user["github_id"]
    regs = await list_registrations(user_id)

    repos = []
    for reg in regs:
        # Get latest analysis for safety score
        analyses = await get_analysis_records(reg.id, limit=1)
        latest = analyses[0] if analyses else None

        repos.append({
            "id": reg.id,
            "owner": reg.owner,
            "repo": reg.repo,
            "full_name": f"{reg.owner}/{reg.repo}",
            "is_active": reg.is_active,
            "last_synced_at": reg.last_synced_at.isoformat() if reg.last_synced_at else None,
            "sync_error": reg.sync_error,
            "latest_score": latest.confidence_score if latest else None,
            "latest_decision": latest.decision if latest else None,
            "latest_analysis_at": latest.created_at.isoformat() if latest else None,
            "created_at": reg.created_at.isoformat() if reg.created_at else None,
        })
    return repos


@router.get("/repos/{reg_id}")
async def dashboard_repo_detail(reg_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    """Get detailed view of a connected repository."""
    user_id = current_user["github_id"]
    reg = await get_registration_by_id(reg_id)

    if not reg or reg.user_id != user_id:
        raise HTTPException(status_code=404, detail="Repository not found")

    analyses = await get_analysis_records(reg_id, limit=20)
    prs = await get_pr_records(reg_id, limit=20)

    return {
        "id": reg.id,
        "owner": reg.owner,
        "repo": reg.repo,
        "full_name": f"{reg.owner}/{reg.repo}",
        "is_active": reg.is_active,
        "last_synced_at": reg.last_synced_at.isoformat() if reg.last_synced_at else None,
        "sync_error": reg.sync_error,
        "created_at": reg.created_at.isoformat() if reg.created_at else None,
        "analyses": [{
            "id": a.id,
            "pr_number": a.pr_number,
            "head_sha": a.head_sha,
            "confidence_score": a.confidence_score,
            "decision": a.decision,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        } for a in analyses],
        "pull_requests": [{
            "id": pr.id,
            "pr_number": pr.pr_number,
            "title": pr.title,
            "state": pr.state,
            "author": pr.author,
            "head_sha": pr.head_sha,
            "created_at": pr.created_at.isoformat() if pr.created_at else None,
        } for pr in prs],
        "safety_trend": _compute_trend(analyses),
    }


@router.get("/repos/{reg_id}/prs")
async def dashboard_repo_prs(reg_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    """List analyzed PRs for a repository."""
    user_id = current_user["github_id"]
    reg = await get_registration_by_id(reg_id)
    if not reg or reg.user_id != user_id:
        raise HTTPException(status_code=404, detail="Repository not found")

    analyses = await get_analysis_records(reg_id, limit=50)
    return [{
        "id": a.id,
        "pr_number": a.pr_number,
        "head_sha": a.head_sha,
        "confidence_score": a.confidence_score,
        "decision": a.decision,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    } for a in analyses]


@router.get("/repos/{reg_id}/prs/{pr_number}")
async def dashboard_pr_detail(
    reg_id: int,
    pr_number: int,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Get full analysis detail for a specific PR."""
    user_id = current_user["github_id"]
    reg = await get_registration_by_id(reg_id)
    if not reg or reg.user_id != user_id:
        raise HTTPException(status_code=404, detail="Repository not found")

    analysis = await get_analysis_by_pr(reg_id, pr_number)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found for this PR")

    evidence = json.loads(analysis.evidence_json) if analysis.evidence_json else []
    security_findings = json.loads(analysis.security_findings_json) if analysis.security_findings_json else []

    # Fix #9: Extract changed files from evidence findings
    # The verification_readiness module stores "Missing test for <file>" findings
    changed_files = []
    for ev in evidence:
        for finding in ev.get("findings", []):
            if finding.startswith("Missing test for "):
                changed_files.append(finding.replace("Missing test for ", ""))
            elif finding.startswith("Deleted test file detected: "):
                changed_files.append(finding.replace("Deleted test file detected: ", ""))

    # Normalize evidence field names for frontend (backend uses module/risk_score_modifier/recommended_action)
    normalized_evidence = []
    for ev in evidence:
        mod_id = ev.get("module", "Unknown")
        modifier = ev.get("risk_modifier") or ev.get("risk_score_modifier", 0)
        points = modifier * MODULE_WEIGHTS.get(mod_id, 0.25)
        normalized_evidence.append({
            "module_name": ev.get("label") or ev.get("module_name") or mod_id,
            "status": ev.get("status", "pass"),
            "risk_modifier": points,
            "findings": ev.get("findings", []),
            "recommendation": ev.get("recommendation") or ev.get("recommended_action", ""),
        })

    # Normalize security findings for frontend (backend uses rule_id/evidence/remediation)
    normalized_security = []
    for sf in security_findings:
        normalized_security.append({
            "title": sf.get("title") or sf.get("rule_id", "Security Finding"),
            "description": sf.get("description") or sf.get("evidence", ""),
            "severity": sf.get("severity", "warning"),
            "file": sf.get("file"),
            "remediation": sf.get("remediation", ""),
            "reference": sf.get("reference", ""),
        })

    decision = analysis.decision or ""

    return {
        "id": analysis.id,
        "pr_number": analysis.pr_number,
        "head_sha": analysis.head_sha,
        "confidence_score": analysis.confidence_score,
        "decision": decision.upper() if decision else "",
        "risk_brief": analysis.risk_brief,
        "rollback_playbook": analysis.rollback_playbook,
        "evidence_results": normalized_evidence,
        "security_findings": normalized_security,
        "changed_files": changed_files,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
    }


def _compute_trend(analyses: list) -> list[dict]:
    """Compute safety score trend from recent analyses."""
    return [
        {
            "date": a.created_at.isoformat() if a.created_at else None,
            "score": a.confidence_score,
            "decision": a.decision,
        }
        for a in reversed(analyses)
    ]
