# Original User Request

## 2026-09-01T01:26:33Z

# Teamwork Project Prompt — Draft

> Status: Launched
> Goal: Craft prompt ? get user approval ? delegate to teamwork_preview
> Requested team: [none — teamwork routes from the description]

Conduct an architectural review, gap analysis, and implementation planning for SafeLane v2 based on the Docs directory, and perform a whole-repo over-engineering audit using the .agents/skills/Ponytail skills. The team should read the source code and tests, reference standard open-source and production-grade patterns, and optionally use external scripts to assist the audit.

Working directory: d:\Development Project\SafeLane v2
Integrity mode: benchmark

## Requirements

### R1. Architecture & Gap Analysis
Produce a comprehensive architectural implementation plan based on the goals in Docs/INSTRUCTIONS_TASKS.md, Docs/CONTEXT.md, and Docs/MASTER_PROMPT.md. The plan must identify the exact gaps between the current codebase state and the finalized Phase 1-7 production architecture.

### R2. Ponytail Repo Audit
Conduct a whole-repo over-engineering and bloat audit strictly applying the principles of the ponytail-audit skill (found in .agents/skills/Ponytail skills). The audit should identify unnecessary abstractions, dead code (like old Prism references or duplicate logic), and over-engineered components.

### R3. Read-Only Deliverables
Generate the findings as markdown artifacts (e.g., rchitecture_plan.md and ponytail_audit_report.md). Do not modify the application's source code during this phase.

## Acceptance Criteria

### Verification Rubric
- [ ] The architecture plan explicitly maps existing code to the 7 phases defined in INSTRUCTIONS_TASKS.md and lists missing components.
- [ ] The Ponytail audit report explicitly identifies instances of over-engineering, bloat, or duplicated logic (e.g., duplicate verdict implementations), applying the lazy-dev principles from the Ponytail skills.
- [ ] Recommendations in the reports reference standard open-source patterns or production-grade practices.
- [ ] No application source code files (.py, .ts, etc.) have been modified.
