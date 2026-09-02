import pytest
from safelane.contracts import EvidenceResult, SecurityFinding, VerdictReport, MODULE_WEIGHTS
from safelane.fabric.verdict import compute_score, decide, build_risk_brief, build_rollback_playbook, build_verdict

@pytest.fixture
def clean_evidence():
    return [
        EvidenceResult(module="change_intelligence", status="pass", risk_score_modifier=0, findings=[], recommended_action=""),
        EvidenceResult(module="incident_memory", status="pass", risk_score_modifier=0, findings=[], recommended_action="")
    ]

@pytest.fixture
def critical_evidence():
    return [
        EvidenceResult(module="change_intelligence", status="critical", risk_score_modifier=100, findings=[], recommended_action="")
    ]

@pytest.mark.unit
def test_module_weights_sum_to_one():
    assert sum(MODULE_WEIGHTS.values()) == 1.0

@pytest.mark.unit
def test_all_pass_results(clean_evidence):
    score, _ = compute_score(clean_evidence)
    assert score == 100
    final_score, decision = decide(score, clean_evidence, [])
    assert final_score == 100
    assert decision == "greenlight"

@pytest.mark.unit
def test_all_critical_results(critical_evidence):
    score, _ = compute_score(critical_evidence)
    assert score < 100
    final_score, decision = decide(score, critical_evidence, [])
    assert decision == "blocked"

@pytest.mark.unit
def test_score_boundary():
    score, decision = decide(69, [], [])
    assert decision == "blocked"
    score, decision = decide(70, [], [])
    assert decision == "greenlight"

@pytest.mark.unit
def test_security_penalty():
    findings = [
        SecurityFinding(rule_id="R1", severity="warning", file="a.py", evidence="", remediation=""),
        SecurityFinding(rule_id="R2", severity="warning", file="b.py", evidence="", remediation="")
    ]
    score, decision = decide(100, [], findings)
    assert score == 84
    
    findings.extend([
        SecurityFinding(rule_id="R3", severity="warning", file="c.py", evidence="", remediation=""),
        SecurityFinding(rule_id="R4", severity="warning", file="d.py", evidence="", remediation=""),
        SecurityFinding(rule_id="R5", severity="warning", file="e.py", evidence="", remediation="")
    ])
    score, decision = decide(100, [], findings)
    assert score == 60
    
@pytest.mark.unit
def test_critical_security():
    findings = [
        SecurityFinding(rule_id="R1", severity="critical", file="a.py", evidence="", remediation="")
    ]
    score, decision = decide(100, [], findings)
    assert decision == "blocked"

@pytest.mark.unit
def test_verdict_playbook_logic():
    report = build_verdict([], [], repo="my-repo", head_sha="abc1234")
    assert report.decision == "greenlight"
    assert report.rollback_playbook is None
    
    findings = [SecurityFinding(rule_id="R1", severity="critical", file="a.py", evidence="", remediation="")]
    report = build_verdict([], findings, repo="my-repo", head_sha="abc1234")
    assert report.decision == "blocked"
    assert report.rollback_playbook is not None
    assert "abc1234" in report.rollback_playbook

@pytest.mark.unit
def test_risk_brief():
    evidence = [EvidenceResult(module="change_intelligence", status="warning", risk_score_modifier=20, findings=["A bad finding"], recommended_action="Fix it")]
    brief = build_risk_brief(evidence, [])
    assert "Change Intelligence" in brief
    assert "A bad finding" in brief
    assert "Fix it" in brief


@pytest.mark.unit
def test_compute_score_breakdown():
    evidence = [
        EvidenceResult(module="change_intelligence", status="warning", risk_score_modifier=20, findings=[], recommended_action=""),
        EvidenceResult(module="incident_memory", status="pass", risk_score_modifier=0, findings=[], recommended_action=""),
        EvidenceResult(module="verification_readiness", status="warning", risk_score_modifier=40, findings=[], recommended_action=""),
        EvidenceResult(module="release_context", status="pass", risk_score_modifier=10, findings=[], recommended_action=""),
    ]
    # Deductions:
    # change_intelligence: 20 * 0.30 = 6.0
    # incident_memory: 0 * 0.25 = 0.0
    # verification_readiness: 40 * 0.25 = 10.0
    # release_context: 10 * 0.20 = 2.0
    # Total deduction = 18.0 -> score = 82
    total, deductions = compute_score(evidence)
    assert total == 82
    assert deductions["change_intelligence"] == 6.0
    assert deductions["incident_memory"] == 0.0
    assert deductions["verification_readiness"] == 10.0
    assert deductions["release_context"] == 2.0


@pytest.mark.unit
def test_verdict_score_breakdown_propagated():
    evidence = [
        EvidenceResult(module="change_intelligence", status="warning", risk_score_modifier=20, findings=[], recommended_action=""),
    ]
    report = build_verdict(evidence, [], repo="test/repo", head_sha="1234567")
    assert report.score_breakdown is not None
    assert "change_intelligence" in report.score_breakdown
    assert report.score_breakdown["change_intelligence"] == 6.0


@pytest.mark.unit
def test_rollback_playbook_branch_strategy():
    playbook = build_rollback_playbook([], repo="my-org/my-repo", head_sha="abc1234567", strategy="branch")
    assert "git checkout -b revert-risky-changes-abc1234" in playbook
    assert "git revert --no-commit abc1234567..HEAD" in playbook
    assert "git push origin revert-risky-changes-abc1234" in playbook


@pytest.mark.unit
def test_rollback_playbook_direct_strategy():
    playbook = build_rollback_playbook([], repo="my-org/my-repo", head_sha="abc1234567", strategy="direct")
    assert "git checkout main" in playbook
    assert "git revert abc1234567 -m 1" in playbook
    assert "git push origin main" in playbook


@pytest.mark.unit
def test_build_verdict_direct_strategy():
    findings = [SecurityFinding(rule_id="R1", severity="critical", file="a.py", evidence="", remediation="")]
    report = build_verdict([], findings, repo="my-repo", head_sha="abc1234", rollback_strategy="direct")
    assert report.decision == "blocked"
    assert "git checkout main" in report.rollback_playbook
    assert "git revert abc1234 -m 1" in report.rollback_playbook


@pytest.mark.unit
def test_risk_brief_with_security_references():
    findings = [
        SecurityFinding(
            rule_id="secret_exposure",
            severity="critical",
            file="config.py",
            evidence="Hardcoded API key",
            remediation="Rotate key",
            reference="https://cwe.mitre.org/data/definitions/798.html"
        )
    ]
    brief = build_risk_brief([], findings)
    assert "[Reference](https://cwe.mitre.org/data/definitions/798.html)" in brief
    assert "CRITICAL" in brief
    assert "secret_exposure" in brief

