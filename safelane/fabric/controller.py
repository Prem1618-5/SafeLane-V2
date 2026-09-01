import asyncio
import logging

from safelane.contracts import (
    AnalysisRequest, RepoContext, EvidenceResult, VerdictReport, PRPayload,
    MODULE_LABELS, MODULE_WEIGHTS, SecurityFinding
)
from safelane.fabric.inputs import clean_untrusted_text, normalize_pr_payload
from safelane.fabric.security_preflight import run_preflight
from safelane.fabric.verdict import build_verdict

# Evidence modules
from safelane.evidence import change_intelligence, incident_memory, verification_readiness, release_context

logger = logging.getLogger('safelane.controller')

MODULE_TIMEOUT_SECONDS = 30

async def run_module(name: str, runner, request: AnalysisRequest, repo_context: RepoContext | None) -> EvidenceResult:
    """Run a single evidence module with timeout and fallback."""
    try:
        return await asyncio.wait_for(
            runner(request, repo_context),
            timeout=MODULE_TIMEOUT_SECONDS
        )
    except Exception as error:
        logger.warning(f"{name} failed: {type(error).__name__}: {error}")
        return EvidenceResult(
            module=name,
            status="warning",
            risk_score_modifier=50,
            findings=[f"{MODULE_LABELS.get(name, name)} could not complete: {type(error).__name__}."],
            recommended_action="Perform manual review before merging.",
        )

async def orchestrate(payload: PRPayload, repo_context: RepoContext | None = None) -> VerdictReport:
    """Full SafeLane pipeline: normalize → preflight → evidence → verdict."""
    # 1. Build AnalysisRequest from PRPayload
    request = AnalysisRequest.from_pr_payload(payload)
    
    # 2. Run Security Preflight (deterministic, before evidence)
    security_findings = run_preflight(
        diff=request.diff,
        changed_files=request.changed_files,
    )
    
    # 3. Dispatch all four Evidence Modules concurrently
    modules = [
        ("change_intelligence", change_intelligence.run),
        ("incident_memory", incident_memory.run),
        ("verification_readiness", verification_readiness.run),
        ("release_context", release_context.run),
    ]
    
    evidence_results = await asyncio.gather(*[
        run_module(name, runner, request, repo_context)
        for name, runner in modules
    ])
    
    # 4. Build verdict using the SINGLE canonical engine
    verdict_report = build_verdict(
        evidence=list(evidence_results),
        security_findings=security_findings,
        repo=payload.repo,
        head_sha=payload.head_sha,
    )
    
    return verdict_report
