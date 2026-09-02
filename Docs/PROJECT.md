# Project: SafeLane v2 Architecture & Ponytail Audit

## Architecture Overview
SafeLane v2 is an AI-assisted GitHub Pull Request safety, pre-deployment risk gating, and engineering intelligence platform.
It combines a deterministic Security Preflight scanner, four specialized evidence modules (Change Intelligence, Incident Memory, Verification Readiness, Release Context), a bounded Control & Evaluation layer, an authoritative canonical Verdict Engine, and a fixed-template GitHub publisher.

## Feature Inventory & Phase Mapping
| # | Feature | Phase | Source | Status |
|---|---------|-------|--------|--------|
| 1 | GitHub Sign-In & OAuth App Flow | Phase 1 (Identity & Ingestion) | INSTRUCTIONS_TASKS.md §2.1 | 🔴 Missing (Only manual PAT login) |
| 2 | Secure Credential Storage & Encryption | Phase 1 (Identity & Ingestion) | INSTRUCTIONS_TASKS.md §2.1 | 🟡 Partial (Plaintext PAT leaked in JWT) |
| 3 | Repository Authorization & Selection | Phase 1 (Identity & Ingestion) | INSTRUCTIONS_TASKS.md §2.1 | 🟡 Partial (Uses PAT from JWT) |
| 4 | Permission Review & Revocation | Phase 1 (Identity & Ingestion) | INSTRUCTIONS_TASKS.md §2.1 | 🟡 Partial (Soft delete only) |
| 5 | Webhook Ingestion & HMAC Verification | Phase 2 (Sync & Engine) | INSTRUCTIONS_TASKS.md §2.2 | 🟡 Partial (Workflow lacks HMAC header) |
| 6 | PR Details & Diff Extraction | Phase 2 (Sync & Engine) | INSTRUCTIONS_TASKS.md §2.2 | 🟡 Partial (Silent empty fallback) |
| 7 | Full Entity Sync (Branches, Commits, Workflows)| Phase 2 (Sync & Engine) | INSTRUCTIONS_TASKS.md §2.2 | 🔴 Missing |
| 8 | Scheduled Background Drift Sync | Phase 2 (Sync & Engine) | INSTRUCTIONS_TASKS.md §2.2 | 🔴 Missing |
| 9 | Orchestrator Agent Concurrency & Budgets | Phase 2 (Sync & Engine) | INSTRUCTIONS_TASKS.md §2.2 | 🟡 Partial (asyncio.gather without token budget) |
| 10| Change Intelligence Diff Analysis | Phase 2 (Sync & Engine) | INSTRUCTIONS_TASKS.md §2.2 | 🟢 Implemented (Regex heuristics + LLM fallback) |
| 11| Incident Memory Retrieval | Phase 2 (Sync & Engine) | INSTRUCTIONS_TASKS.md §2.2 | 🟡 Partial (Azure Search/mock; lacks Qdrant) |
| 12| Verification Readiness Test Inspection | Phase 2 (Sync & Engine) | INSTRUCTIONS_TASKS.md §2.2 | 🟢 Implemented |
| 13| Release Context Calendar Evaluation | Phase 2 (Sync & Engine) | INSTRUCTIONS_TASKS.md §2.2 | 🟢 Implemented |
| 14| Output Schema & Quality Evaluation | Phase 3 (Evaluation & Dash) | INSTRUCTIONS_TASKS.md §2.3 | 🔴 Missing (Foundry evaluate_quality is empty stub) |
| 15| Dashboard UI & Repository Safety Metrics | Phase 3 (Evaluation & Dash) | INSTRUCTIONS_TASKS.md §2.3 | 🔴 Missing (Frontend has no dashboard) |
| 16| Deterministic Security Preflight Scanner | Phase 4 (Policy & Workspace)| INSTRUCTIONS_TASKS.md §2.4 | 🟢 Implemented (Regex rules for secrets, eval, etc.)|
| 17| Authoritative Policy & Verdict Engine | Phase 4 (Policy & Workspace)| INSTRUCTIONS_TASKS.md §2.4 | 🟡 Partial (Duplicate conflicting logic in controller)|
| 18| Fixed-Template GitHub PR Publisher | Phase 4 (Policy & Workspace)| INSTRUCTIONS_TASKS.md §2.4 | 🟢 Implemented (Fixed template + @copilot nudge) |
| 19| Repository Workspace UI & Findings View | Phase 4 (Policy & Workspace)| INSTRUCTIONS_TASKS.md §2.4 | 🔴 Missing |
| 20| PostgreSQL Relational Schema & Migrations | Phase 5 (Persistence & Telemetry)| INSTRUCTIONS_TASKS.md §2.5 | 🟡 Partial (Only 2 basic tables, no Alembic) |
| 21| Qdrant Semantic Incident Memory Store | Phase 5 (Persistence & Telemetry)| INSTRUCTIONS_TASKS.md §2.5 | 🔴 Missing |
| 22| Activity Timeline & In-App Notifications | Phase 5 (Persistence & Telemetry)| INSTRUCTIONS_TASKS.md §2.5 | 🔴 Missing |
| 23| OpenTelemetry Distributed Tracing | Phase 5 (Persistence & Telemetry)| INSTRUCTIONS_TASKS.md §2.5 | 🟡 Partial (Foundry helpers disconnected) |
| 24| Long-Term Analytics & Safety Trends | Phase 6 (DX & Analytics) | INSTRUCTIONS_TASKS.md §2.6 | 🔴 Missing |
| 25| Developer CLI (`safelane check`) | Phase 6 (DX & Analytics) | INSTRUCTIONS_TASKS.md §2.6 | 🔴 Missing |
| 26| Interactive Commit / Branch Graph UI | Phase 7 (Hardening & Graph) | INSTRUCTIONS_TASKS.md §2.7 | 🔴 Missing |
| 27| Production Hardening (CORS, CSRF, Rate Limit)| Phase 7 (Hardening & Graph) | INSTRUCTIONS_TASKS.md §2.7 | 🔴 Missing (Wildcard CORS) |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Survey & Technical Investigation | Deep survey of codebase, spec mining, Ponytail bloat audit | none | DONE |
| 2 | Deliverables Drafting | Generate `architecture_plan.md` and `ponytail_audit_report.md` | M1 | DONE |
| 3 | Multi-Angle Review & Verification | Independent Reviewers + Challengers + Forensic Auditor | M2 | DONE |
| 4 | Final Synthesis & Parent Reporting | Comprehensive final report back to caller | M3 | DONE |

## Code Layout & Boundaries
- `architecture_plan.md` — Master Architecture Implementation Plan (Phases 1-7, gap analysis, open-source references)
- `ponytail_audit_report.md` — Whole-Repo Ponytail Bloat & Over-Engineering Audit Report
- `.agents/` — Agent coordination, briefing, handoffs, and audit logs
- `safelane/`, `platform/`, `function_deploy/`, `mcp_servers/`, `tests/` — Application source code (READ-ONLY)
