import asyncio
import logging
import re
from pathlib import Path

from safelane.contracts import AnalysisRequest, RepoContext, EvidenceResult, SecurityFinding
from safelane.evidence.incident_store import get_mock_incidents

logger = logging.getLogger('safelane.incident_memory')


def derive_index_name(owner: str, repo: str) -> str:
    name = f"{owner}-{repo}".lower()
    return re.sub(r'[^a-z0-9\-]', '-', name)


def _match_incident_to_files(changed_files: list[str], mock_incidents: list) -> list:
    matched = []
    seen = set()
    for incident in mock_incidents:
        for f in changed_files:
            p = Path(f)
            basename = p.name
            stem = p.stem

            for af in incident.affected_files:
                af_p = Path(af)
                if f == af or basename == af_p.name or stem == af_p.stem:
                    if incident.id not in seen:
                        seen.add(incident.id)
                        matched.append(incident)
    matched.sort(key=lambda x: x.timestamp, reverse=True)
    return matched


async def _search_qdrant(changed_files: list[str], qdrant_url: str, qdrant_api_key: str | None, collection: str) -> list:
    """Search Qdrant for incidents related to changed files using semantic embeddings."""
    try:
        import os
        from qdrant_client import AsyncQdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        from safelane.evidence.incident_store import IncidentRecord

        openai_key = os.environ.get("AZURE_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        embed_deployment = os.environ.get("AZURE_OPENAI_EMBED_DEPLOYMENT", "text-embedding-3-small")

        if not openai_key:
            logger.warning("No OpenAI/Azure key for embeddings — skipping Qdrant vector search.")
            return []

        # Generate query embedding for the changed file paths
        query_text = " ".join(changed_files[:20])  # cap at 20 files for token budget

        from openai import AsyncAzureOpenAI, AsyncOpenAI
        if azure_endpoint:
            client = AsyncAzureOpenAI(
                api_key=openai_key,
                azure_endpoint=azure_endpoint,
                api_version="2024-02-01",
            )
        else:
            client = AsyncOpenAI(api_key=openai_key)

        embed_resp = await client.embeddings.create(
            model=embed_deployment,
            input=query_text,
        )
        query_vector = embed_resp.data[0].embedding

        # Query Qdrant
        qdrant = AsyncQdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        hits = await qdrant.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=10,
            score_threshold=0.65,
        )

        results = []
        seen = set()
        for hit in hits:
            payload = hit.payload or {}
            inc_id = payload.get("id", str(hit.id))
            if inc_id not in seen:
                seen.add(inc_id)
                results.append(IncidentRecord(
                    id=inc_id,
                    title=payload.get("title", "Unknown incident"),
                    severity=payload.get("severity", "warning"),
                    affected_files=payload.get("affected_files", []),
                    timestamp=payload.get("timestamp", ""),
                    summary=payload.get("summary", ""),
                ))
        return results

    except Exception as e:
        logger.warning(f"Qdrant search failed: {e}")
        return []


async def run(request: AnalysisRequest, repo_context: RepoContext | None = None) -> EvidenceResult:
    import os

    qdrant_url = os.environ.get("QDRANT_URL")
    qdrant_api_key = os.environ.get("QDRANT_API_KEY")
    use_mock = os.environ.get("INCIDENT_MEMORY_MOCK") == "true"

    # ── Path 1: Qdrant vector search (production) ────────────────────────────
    if qdrant_url and not use_mock:
        collection = derive_index_name(
            repo_context.owner if repo_context else "default",
            repo_context.repo if repo_context else "repo",
        )
        incidents = await _search_qdrant(
            request.changed_files, qdrant_url, qdrant_api_key, collection
        )
    # ── Path 2: Legacy Azure Search (if repo_context carries azure config) ──
    elif repo_context and repo_context.azure_search_endpoint and repo_context.azure_search_endpoint != "mock":
        try:
            from safelane.evidence.incident_store import search_incidents
            index_name = derive_index_name(repo_context.owner, repo_context.repo)
            incidents = await asyncio.to_thread(
                search_incidents,
                request.changed_files,
                repo_context.azure_search_endpoint,
                repo_context.azure_search_key,
                index_name,
            )
        except Exception as e:
            logger.warning(f"Azure incident search failed: {e}")
            return EvidenceResult(
                module="incident_memory",
                status="warning",
                risk_score_modifier=10,
                findings=["Incident search temporarily unavailable — could not query incident history."],
                recommended_action="Review manually if critical files are touched.",
            )
    # ── Path 3: Mock data (local dev / demo mode) ─────────────────────────────
    elif use_mock or (repo_context and repo_context.azure_search_endpoint == "mock"):
        mock_incidents = get_mock_incidents()
        incidents = _match_incident_to_files(request.changed_files, mock_incidents)
    # ── Path 4: No incident store configured — safe skip ─────────────────────
    else:
        return EvidenceResult(
            module="incident_memory",
            status="pass",
            risk_score_modifier=0,
            findings=["No incident memory store configured — no relevant incident history available."],
            recommended_action="Configure QDRANT_URL to enable semantic incident history.",
        )

    if not incidents:
        return EvidenceResult(
            module="incident_memory",
            status="pass",
            risk_score_modifier=0,
            findings=[],
            recommended_action="",
        )

    findings = []
    has_critical = False

    for inc in incidents:
        if inc.severity == "critical":
            has_critical = True
        findings.append(f"PREVIOUS_INCIDENT_{inc.id} ({inc.severity}): {inc.title} — {inc.summary}")

    if len(incidents) >= 3 or has_critical:
        status = "critical"
        risk_score_modifier = 60
    else:
        status = "warning"
        risk_score_modifier = 30

    return EvidenceResult(
        module="incident_memory",
        status=status,
        risk_score_modifier=risk_score_modifier,
        findings=findings,
        recommended_action="Review related incidents carefully before approving.",
    )
