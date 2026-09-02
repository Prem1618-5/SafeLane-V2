import logging
import httpx
from pathlib import Path

from safelane.contracts import AnalysisRequest, RepoContext, EvidenceResult

logger = logging.getLogger('safelane.verification_readiness')


def get_expected_test_paths(file_path: str) -> list[str]:
    path = Path(file_path)
    basename = path.name
    stem = path.stem
    ext = path.suffix
    
    possible_paths = []
    if ext == ".py":
        expected_name = f"test_{basename}"
        possible_paths = [
            f"tests/{expected_name}",
            f"tests/{path.parent}/{expected_name}",
            f"tests/{path.parent.name}/{expected_name}",
            f"{path.parent}/test_{basename}"
        ]
    elif ext in [".js", ".jsx", ".ts", ".tsx"]:
        possible_paths = [
            f"{path.parent}/__tests__/{basename}",
            f"{path.parent}/{stem}.test{ext}",
            f"{path.parent}/{stem}.spec{ext}",
            f"tests/{stem}.test{ext}"
        ]
    elif ext == ".go":
        possible_paths = [
            f"{path.parent}/{stem}_test.go"
        ]
    return possible_paths

def is_test_file(file_path: str) -> bool:
    path = Path(file_path)
    if path.suffix == ".py" and (path.name.startswith("test_") or path.name.endswith("_test.py")):
        return True
    if path.suffix in [".js", ".jsx", ".ts", ".tsx"] and (".test." in path.name or ".spec." in path.name or "__tests__" in path.parts):
        return True
    if path.suffix == ".go" and path.name.endswith("_test.go"):
        return True
    return False

async def run(request: AnalysisRequest, repo_context: RepoContext | None = None) -> EvidenceResult:

    if not repo_context or not repo_context.gh_token:
        return EvidenceResult(
            module="verification_readiness",
            status="warning",
            risk_score_modifier=25,
            findings=["No GitHub token — cannot verify test coverage"],
            recommended_action="Manual test review recommended"
        )

    findings = []
    missing_tests = 0
    deleted_tests = 0

    # 1. Detect deleted test files
    for file_path in request.changed_files:
        if is_test_file(file_path):
            if f"--- a/{file_path}" in request.diff and "+++ /dev/null" in request.diff:
                deleted_tests += 1
                findings.append(f"Deleted test file detected: {file_path}")

    # 2. Check changed source files for missing tests
    changed_src_files = [
        f for f in request.changed_files
        if Path(f).suffix in [".py", ".js", ".jsx", ".ts", ".tsx", ".go"]
        and not Path(f).name.endswith("__init__.py")
        and not is_test_file(f)
    ]

    repository = request.repository or f"{repo_context.owner}/{repo_context.repo}"

    async with httpx.AsyncClient(
        headers={
            "Authorization": f"Bearer {repo_context.gh_token}",
            "Accept": "application/vnd.github.v3+json"
        },
        timeout=10.0
    ) as client:
        for f in changed_src_files:
            possible_paths = get_expected_test_paths(f)
            if not possible_paths:
                continue
                
            test_exists = False
            try:
                for p in possible_paths:
                    p = p.replace("\\\\", "/").replace("//", "/")
                    resp = await client.get(f"https://api.github.com/repos/{repository}/contents/{p}")
                    if resp.status_code == 200:
                        test_exists = True
                        break
                    elif resp.status_code == 404:
                        continue
                    else:
                        resp.raise_for_status()
            except httpx.HTTPError as e:
                logger.warning(f"GitHub API error checking {f}: {e}")
                return EvidenceResult(
                    module="verification_readiness",
                    status="warning",
                    risk_score_modifier=25,
                    findings=["GitHub API error — manual test review recommended"],
                    recommended_action="Manual test review recommended"
                )

            if not test_exists:
                missing_tests += 1
                findings.append(f"Missing test for {f}")

    # 3. Scoring
    score = 0
    status = "pass"
    if missing_tests == 0 and deleted_tests == 0:
        score = 0
        status = "pass"
    elif missing_tests in (1, 2) and deleted_tests == 0:
        score = 30
        status = "warning"
    else:
        # 3+ missing tests or any deleted test files
        score = 60
        status = "critical"

    return EvidenceResult(
        module="verification_readiness",
        status=status,
        risk_score_modifier=score,
        findings=findings,
        recommended_action="Add tests for changed files"
    )
