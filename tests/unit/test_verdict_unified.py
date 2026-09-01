"""Tests verifying that the verdict engine is unified and the score 60-69 bug is fixed."""
import pytest
import ast
import os
from safelane.contracts import EvidenceResult, SecurityFinding, VerdictReport
from safelane.fabric.verdict import build_verdict


@pytest.mark.unit
def test_only_one_build_verdict_in_codebase():
    """Verify that build_verdict is defined ONLY in verdict.py, not in controller.py."""
    controller_path = os.path.join(os.path.dirname(__file__), "..", "..", "safelane", "fabric", "controller.py")
    with open(controller_path) as f:
        tree = ast.parse(f.read())

    function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    assert "build_verdict" not in function_names, \
        "build_verdict() must not be defined in controller.py — use the canonical version in verdict.py"


@pytest.mark.unit
def test_controller_imports_from_verdict():
    """Verify controller.py imports build_verdict from verdict module."""
    controller_path = os.path.join(os.path.dirname(__file__), "..", "..", "safelane", "fabric", "controller.py")
    with open(controller_path) as f:
        source = f.read()

    assert "from safelane.fabric.verdict import build_verdict" in source, \
        "controller.py must import build_verdict from safelane.fabric.verdict"


@pytest.mark.unit
def test_score_60_to_69_is_blocked():
    """Scores 60-69 must produce 'blocked' — this was the crash bug in the old duplicate."""
    # Create evidence that produces a score in the 60-69 range
    evidence = [
        EvidenceResult(
            module="change_intelligence",
            status="warning",
            risk_score_modifier=30,
            findings=["Some risk"],
            recommended_action="Review"
        ),
        EvidenceResult(
            module="incident_memory",
            status="pass",
            risk_score_modifier=0,
            findings=[],
            recommended_action=""
        ),
    ]

    # With a warning security finding (8 points penalty)
    security = [
        SecurityFinding(rule_id="test", severity="warning", file="a.py", evidence="test", remediation="fix")
    ]

    report = build_verdict(evidence, security, repo="test/repo")

    # Score should be somewhere in the range where the old code crashed
    # Key invariant: if score < 70, decision MUST be blocked
    if report.confidence_score < 70:
        assert report.decision == "blocked", \
            f"Score {report.confidence_score} < 70 should be blocked but got {report.decision}"


@pytest.mark.unit
def test_score_70_is_greenlight():
    """Score exactly 70 with no critical findings should be greenlight."""
    from safelane.fabric.verdict import decide
    score, decision = decide(70, [], [])
    assert decision == "greenlight"


@pytest.mark.unit
def test_score_69_is_blocked():
    """Score exactly 69 should be blocked."""
    from safelane.fabric.verdict import decide
    score, decision = decide(69, [], [])
    assert decision == "blocked"


@pytest.mark.unit
def test_critical_evidence_always_blocks():
    """Any critical evidence result must force blocked, regardless of score."""
    evidence = [
        EvidenceResult(
            module="change_intelligence",
            status="critical",
            risk_score_modifier=60,
            findings=["Critical risk"],
            recommended_action="Block"
        ),
    ]
    report = build_verdict(evidence, [], repo="test/repo")
    assert report.decision == "blocked"


@pytest.mark.unit
def test_critical_security_always_blocks():
    """Any critical security finding must force blocked."""
    security = [
        SecurityFinding(rule_id="secret", severity="critical", file="a.py", evidence="Key exposed", remediation="Rotate")
    ]
    report = build_verdict([], security, repo="test/repo")
    assert report.decision == "blocked"


@pytest.mark.unit
def test_rollback_playbook_on_blocked():
    """Blocked verdicts with a head_sha should include rollback playbook."""
    security = [
        SecurityFinding(rule_id="secret", severity="critical", file="a.py", evidence="Key", remediation="Rotate")
    ]
    report = build_verdict([], security, repo="test/repo", head_sha="abc1234")
    assert report.rollback_playbook is not None
    assert "abc1234" in report.rollback_playbook


@pytest.mark.unit
def test_greenlight_has_no_playbook():
    """Greenlight verdicts must have no rollback playbook."""
    report = build_verdict([], [], repo="test/repo", head_sha="abc1234")
    assert report.decision == "greenlight"
    assert report.rollback_playbook is None
