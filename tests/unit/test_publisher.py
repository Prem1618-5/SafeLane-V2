import pytest
from safelane.contracts import VerdictReport, EvidenceResult
from safelane.fabric.publisher import render_comment, table_cell

@pytest.mark.unit
def test_table_cell_sanitization():
    assert table_cell("Normal string") == "Normal string"
    assert table_cell("Has | pipes | inside") == "Has \\| pipes \\| inside"
    assert table_cell("   Extra   spaces   ") == "Extra spaces"
    assert table_cell("a" * 200, limit=10) == "aaaaaaaaaa"
    assert table_cell("") == ""

@pytest.mark.unit
def test_render_comment_greenlight():
    report = VerdictReport(
        confidence_score=95,
        decision="greenlight",
        risk_brief="Looking good",
        rollback_playbook=None,
        evidence_results=[
            EvidenceResult(
                module="change_intelligence",
                status="pass",
                risk_score_modifier=0,
                findings=["Looks great"],
                recommended_action="None"
            )
        ],
        security_findings=[]
    )
    comment = render_comment(report)
    assert "Change Intelligence" in comment
    assert "GREENLIGHT" in comment
    assert "Looking good" in comment
    assert "Should not be visible" not in comment
    assert "Rollback Playbook" not in comment

@pytest.mark.unit
def test_render_comment_blocked():
    report = VerdictReport(
        confidence_score=40,
        decision="blocked",
        risk_brief="Too risky",
        rollback_playbook="Revert immediately",
        evidence_results=[
            EvidenceResult(
                module="incident_memory",
                status="critical",
                risk_score_modifier=40,
                findings=["Past incident matched: | severe |"],
                recommended_action="Fix it"
            )
        ],
        security_findings=[]
    )
    comment = render_comment(report)
    assert "Incident Memory" in comment
    assert "BLOCKED" in comment
    assert "Too risky" in comment
    assert "Rollback Playbook" in comment
    assert "Revert immediately" in comment
    assert "\\| severe \\|" in comment # Sanitized

@pytest.mark.unit
def test_raw_content_never_in_output():
    report = VerdictReport(
        confidence_score=100,
        decision="greenlight",
        risk_brief="Brief",
        rollback_playbook=None,
        evidence_results=[],
        security_findings=[]
    )
    comment = render_comment(report)
    assert "raw diff" not in comment


@pytest.mark.unit
def test_render_comment_table_headers_and_points_deducted():
    report = VerdictReport(
        confidence_score=82,
        decision="greenlight",
        risk_brief="Low risk",
        rollback_playbook=None,
        evidence_results=[
            EvidenceResult(
                module="change_intelligence",
                status="warning",
                risk_score_modifier=20,
                findings=["2 changed files without coverage"],
                recommended_action="Review"
            ),
            EvidenceResult(
                module="release_context",
                status="pass",
                risk_score_modifier=0,
                findings=[],
                recommended_action=""
            )
        ],
        security_findings=[],
        score_breakdown={"change_intelligence": 6.0, "release_context": 0.0}
    )
    comment = render_comment(report)
    assert "| Evidence Module | Status | Points Deducted | Key Finding |" in comment
    assert "| Change Intelligence | warning | -6.0 | 2 changed files without coverage |" in comment
    assert "| Release Context | pass | -0.0 | No issues found |" in comment

