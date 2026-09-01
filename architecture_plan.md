# SafeLane v2 — Master Architecture Implementation Plan

**Document Version:** 2.0.0-PROD  
**Author:** SafeLane Architecture & Engineering Team  
**Date:** 2026-09-01  
**Project:** SafeLane v2 — AI-Assisted GitHub Pull Request Safety, Pre-Deployment Risk Gate & Engineering Intelligence Platform  
**Target Codebase:** `d:\Development Project\SafeLane v2`  
**Status:** Authoritative Architectural Implementation Plan & Production Blueprint  

---

## Table of Contents

1. [Executive Summary & System Architecture](#1-executive-summary--system-architecture)
   - 1.1 [System Vision & Purpose](#11-system-vision--purpose)
   - 1.2 [High-Level Architecture: Target vs. Current Delta](#12-high-level-architecture-target-vs-current-delta)
   - 1.3 [Core Invariants & Design Principles](#13-core-invariants--design-principles)
2. [Traceability & Gap Analysis Matrices](#2-traceability--gap-analysis-matrices)
   - 2.1 [Complete 27-Feature Traceability Matrix (Phases 1–7)](#21-complete-27-feature-traceability-matrix-phases-17)
   - 2.2 [Confirmed 22-Problem Ledger & Root Cause Mapping](#22-confirmed-22-problem-ledger--root-cause-mapping)
   - 2.3 [Edge Cases & Failure Modes Analysis](#23-edge-cases--failure-modes-analysis)
3. [Industry Standards & Open-Source Benchmark Comparisons](#3-industry-standards--open-source-benchmark-comparisons)
   - 3.1 [Guardrails AI & NeMo Guardrails (Three-Tier Validation Rails)](#31-guardrails-ai--nemo-guardrails-three-tier-validation-rails)
   - 3.2 [LiteLLM, Instructor & Pydantic v2 (Structured Schema & Token Budgets)](#32-litellm-instructor--pydantic-v2-structured-schema--token-budgets)
   - 3.3 [FastAPI Production Standards (Unified Modular Application)](#33-fastapi-production-standards-unified-modular-application)
   - 3.4 [PostgreSQL 16 + AsyncPG Connection Pooling](#34-postgresql-16--asyncpg-connection-pooling)
   - 3.5 [Qdrant Vector Database (Incident Semantic Retrieval)](#35-qdrant-vector-database-incident-semantic-retrieval)
   - 3.6 [OpenTelemetry & W3C Distributed Tracing](#36-opentelemetry--w3c-distributed-tracing)
4. [Phase-by-Phase Comprehensive Technical Specifications](#4-phase-by-phase-comprehensive-technical-specifications)
   - 4.1 [Phase 1: Core Architecture, GitHub Identity & Ingestion](#41-phase-1-core-architecture-github-identity--ingestion)
   - 4.2 [Phase 2: Execution Engine, Synchronization & Multi-LLM Routing](#42-phase-2-execution-engine-synchronization--multi-llm-routing)
   - 4.3 [Phase 3: Control & Evaluation Suite, Verification Logic & Dashboard](#43-phase-3-control--evaluation-suite-verification-logic--dashboard)
   - 4.4 [Phase 4: Authoritative Policy Engine, Security Preflight & Repository Workspace](#44-phase-4-authoritative-policy-engine-security-preflight--repository-workspace)
   - 4.5 [Phase 5: Durable Persistence, Qdrant Vector Memory & Unified Timeline](#45-phase-5-durable-persistence-qdrant-vector-memory--unified-timeline)
   - 4.6 [Phase 6: Developer Experience, CLI & Long-Term Analytics](#46-phase-6-developer-experience-cli--long-term-analytics)
   - 4.7 [Phase 7: Production Hardening, Graph Visualization & Benchmarking](#47-phase-7-production-hardening-graph-visualization--benchmarking)
5. [Complete Data Architecture](#5-complete-data-architecture)
   - 5.1 [PostgreSQL Relational Schema (Complete SQL DDL)](#51-postgresql-relational-schema-complete-sql-ddl)
   - 5.2 [Qdrant Vector Collection Architecture](#52-qdrant-vector-collection-architecture)
6. [Async Pipeline, Concurrency & Resilience Model](#6-async-pipeline-concurrency--resilience-model)
   - 6.1 [End-to-End Event Flow & Execution Timeline](#61-end-to-end-event-flow--execution-timeline)
   - 6.2 [Bounded Execution & Reliability Matrix](#62-bounded-execution--reliability-matrix)
   - 6.3 [Canonical Verdict Decision State Machine](#63-canonical-verdict-decision-state-machine)
7. [Observability, Telemetry & Evaluation Framework](#7-observability-telemetry--evaluation-framework)
   - 7.1 [OpenTelemetry Span Hierarchy & Semantic Conventions](#71-opentelemetry-span-hierarchy--semantic-conventions)
   - 7.2 [Prometheus Metrics Specifications](#72-prometheus-metrics-specifications)
   - 7.3 [Agent Evaluation & Bounded Feedback Loop](#73-agent-evaluation--bounded-feedback-loop)
8. [Implementation Strategy, Risk Analysis & Definition of Done](#8-implementation-strategy-risk-analysis--definition-of-done)
   - 8.1 [Phased Execution Order & Dependencies](#81-phased-execution-order--dependencies)
   - 8.2 [Integration-First Verification Rules](#82-integration-first-verification-rules)
   - 8.3 [Definition of Done Checklist](#83-definition-of-done-checklist)

---

## 1. Executive Summary & System Architecture

### 1.1 System Vision & Purpose

SafeLane v2 is an enterprise-grade, AI-assisted GitHub Pull Request safety, pre-deployment risk gating, and engineering intelligence platform. In modern DevOps workflows, continuous integration runs unit tests and linters, but fails to capture complex operational, architectural, and behavioral failure modes such as:
- Subtle schema drops or unindexed table alterations in database migrations.
- Missing retry logic, broken error handling, or silent exception swallows in distributed systems.
- Deployments initiated during dangerous operational freeze windows (Friday afternoons, holidays).
- Missing test suites for modified high-risk modules.
- Re-introduction of known bugs from past production incidents.
- Hardcoded secrets, unpinned CI/CD actions, `eval`/`exec` injections, or prompt injection payloads.

SafeLane bridges this critical gap by combining:
1. **Deterministic Security Preflight Scanner**: Fast regex and AST-based static safety rules that strictly override AI reasoning.
2. **Four Multi-Angle Evidence Modules**: Change Intelligence, Incident Memory (Qdrant semantic vector search), Verification Readiness, and Release Context.
3. **Bounded Control & Evaluation Layer**: Schema validation, token/time budget enforcement, and self-correction loops.
4. **Single Canonical Verdict Engine**: Authoritative calculation of deployment risk scores (0–100) and actionable decisions (`GREENLIGHT`, `WARNING`, `BLOCK`, `INSUFFICIENT_ANALYSIS`).
5. **Fixed-Template GitHub Publisher & Copilot Nudger**: Clear, reproducible markdown commentary and automated `@copilot` test generation nudges.

### 1.2 High-Level Architecture: Target vs. Current Delta

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TARGET PRODUCTION ARCHITECTURE                                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘

       ┌───────────────────────────────┐               ┌────────────────────────────────┐
       │   GitHub Webhooks & Events    │               │     Developer / UI Client      │
       │ (PR open/sync, Workflow runs) │               │   (React / Tailwind Dashboard) │
       └──────────────┬────────────────┘               └───────────────┬────────────────┘
                      │ HMAC SHA-256 Verified                          │ JWT Bearer (HttpOnly)
                      ▼                                                ▼
       ┌────────────────────────────────────────────────────────────────────────────────┐
       │                       UNIFIED FASTAPI APPLICATION GATEWAY                      │
       │  ┌───────────────────────┬──────────────────────────┬────────────────────────┐ │
       │  │  /api/v1/auth         │  /api/v1/github          │  /api/v1/registrations │ │
       │  │  (OAuth / App Auth)   │  (Sync & Webhooks)       │  (Repo Management)     │ │
       │  ├───────────────────────┼──────────────────────────┼────────────────────────┤ │
       │  │  /api/v1/dashboard    │  /api/v1/workspace       │  /api/v1/analytics     │ │
       │  │  (Metrics & Score)    │  (PR Findings & Diffs)   │  (Trends & Reports)    │ │
       │  ├───────────────────────┴──────────────────────────┴────────────────────────┤ │
       │  │  /webhook/github (Direct GitHub Webhook Ingestion, 202 Accepted Response) │ │
       │  └───────────────────────────────────────────────────────────────────────────┘ │
       └──────────────────────────────┬─────────────────────────────────────────────────┘
                                      │ Ingest Event & Trigger Background Job
                                      ▼
       ┌────────────────────────────────────────────────────────────────────────────────┐
       │                        ASYNC ORCHESTRATION PIPELINE                            │
       │                                                                                │
       │  ┌──────────────────────────────────────────────────────────────────────────┐  │
       │  │ 1. Context Builder & Ingestion Validator (inputs.py)                     │  │
       │  │    - Fetch PR diff, commit history, changed files from GitHub API        │  │
       │  │    - Clean untrusted text (NFKC, null strip, size caps: 200k diff/1k path)│  │
       │  │    - Load DB Registration Context (credentials, tenant settings)         │  │
       │  └─────────────────────────────────────┬────────────────────────────────────┘  │
       │                                        │                                       │
       │                                        ▼                                       │
       │  ┌──────────────────────────────────────────────────────────────────────────┐  │
       │  │ 2. Deterministic Security Preflight Scanner (security_preflight.py)      │  │
       │  │    - Secrets (API Keys, PEMs, AWS)   - Dynamic Code Exec (eval, exec)    │  │
       │  │    - CI/CD Hardening (write-all, unpinned actions) - Prompt Injection    │  │
       │  └─────────────────────────────────────┬────────────────────────────────────┘  │
       │                                        │                                       │
       │                                        ▼                                       │
       │  ┌──────────────────────────────────────────────────────────────────────────┐  │
       │  │ 3. Parallel Evidence Gathering (Bounded Concurrency & Timeouts)          │  │
       │  │    ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────────┐  │  │
       │  │    │ Change Intel.    │  │ Incident Memory  │  │ Verification Readiness│  │  │
       │  │    │ (Diff heuristics │  │ (Qdrant Semantic │  │ (Test coverage &      │  │  │
       │  │    │  + LLM summary)  │  │  Vector Search)  │  │  deleted tests check) │  │  │
       │  │    └────────┬─────────┘  └────────┬─────────┘  └───────────┬───────────┘  │  │
       │  │             │                     │                        │              │  │
       │  │             └─────────────────────┼────────────────────────┘              │  │
       │  │                                   ▼                                       │  │
       │  │                          ┌──────────────────┐                             │  │
       │  │                          │ Release Context  │                             │  │
       │  │                          │ (Holiday/Weekend │                             │  │
       │  │                          │  Calendar logic) │                             │  │
       │  │                          └────────┬─────────┘                             │  │
       │  └───────────────────────────────────┼───────────────────────────────────────┘  │
       │                                      │                                         │
       │                                      ▼                                         │
       │  ┌──────────────────────────────────────────────────────────────────────────┐  │
       │  │ 4. Control & Evaluation Layer (Bounded Iterations, Max 2 Retries)        │  │
       │  │    - Pydantic v2 Schema validation & Evidence Grounding Check            │  │
       │  │    - Token / Time budget verification (fail to INSUFFICIENT_ANALYSIS)    │  │
       │  └───────────────────────────────────┼───────────────────────────────────────┘  │
       │                                      │                                         │
       │                                      ▼                                         │
       │  ┌──────────────────────────────────────────────────────────────────────────┐  │
       │  │ 5. Canonical Deterministic Verdict & Policy Engine (verdict.py)          │  │
       │  │    - Weighted base scoring: CI (30%) + IM (25%) + VR (25%) + RC (20%)    │  │
       │  │    - Authoritative Security Penalties & Hard Blocker Rules               │  │
       │  │    - Decision States: GREENLIGHT | WARNING | BLOCK | INSUFFICIENT_ANALYSIS│  │
       │  │    - Dynamic Rollback Playbook generator (for BLOCKED state)             │  │
       │  └───────────────────────────────────┬───────────────────────────────────────┘  │
       └──────────────────────────────────────┼─────────────────────────────────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
       ┌──────────────────────────────┐                ┌────────────────────────────────┐
       │     DURABLE PERSISTENCE      │                │       EXTERNAL PUBLISHING      │
       │  - PostgreSQL 16 (AsyncPG)   │                │  - Fixed-Template PR Comment   │
       │    (Analyses, Findings, PRs, │                │  - Commit Check Status API     │
       │     Verdicts, Notifications) │                │  - Copilot Test Generation     │
       │  - Qdrant Vector Store       │                │    Nudge (@copilot comment)    │
       │    (Incident Memory Embeds)  │                │  - OpenTelemetry Trace Export  │
       └──────────────────────────────┘                └────────────────────────────────┘
```

#### Comparison of Current Prototype vs. Target State:

```text
Dimension              Current Prototype State                         Target Production State
────────────────────────────────────────────────────────────────────────────────────────────────────────
Architecture Model     Split-brain (Port 8000 Fabric + Port 8080)     Unified Modular FastAPI Application
Authentication         Manual PAT input; Plaintext PAT in JWT          GitHub OAuth 2.0 PKCE / GitHub App Flow
Event Ingestion        Actions workflow curling webhook (No HMAC)      Direct signed Webhooks (HMAC SHA-256)
Verdict Engine         DUPLICATE conflicting engines (<60 vs <70)      Single Canonical Engine (verdict.py)
Incident Memory        Azure Search lexical / hardcoded mocks          Qdrant Semantic Vector Database
Database & Models      SQLite/Postgres create_all (2 tables only)      PostgreSQL 16 + AsyncPG + Alembic (9 tables)
UI & Workspace         3-Step PAT Setup Wizard (index.html only)       Full Dashboard, Workspace, Timeline UI
Observability          Disconnected Foundry/OTel helper stubs          Live OpenTelemetry Spans & Prometheus
Agent Control          No token budgeting; no evaluation/retry         Bounded Evaluation Rail & Retry Feedback
```

### 1.3 Core Invariants & Design Principles

1. **Deterministic Override**: AI models generate evidence and summaries, but never determine the final verdict score or decision. Deterministic Security Preflight and canonical policy math remain absolute.
2. **Never Fabricate Evidence**: If external services (GitHub API, Qdrant, LLM) fail or time out, the system degrades gracefully to explicit warnings or `INSUFFICIENT_ANALYSIS` without making speculative assertions.
3. **Zero Secret Exposure**: Passwords, PATs, and webhook secrets exist only in backend encrypted storage (Fernet / AES-256-GCM). Tokens are never placed in browser-accessible JWT payloads, URL parameters, or client-side storage.
4. **Bounded AI Execution**: Every agent call has strict timeouts, token caps, retry ceilings (max 2 iterations), and execution budgets. Runaway loops are mathematically impossible.
5. **Single Verdict Authority**: Only `safelane/fabric/verdict.py` may calculate confidence scores, apply module weights, apply security penalties, and construct the `VerdictReport`.

---

## 2. Traceability & Gap Analysis Matrices

### 2.1 Complete 27-Feature Traceability Matrix (Phases 1–7)

| # | Phase | Feature Name | Description | Inputs | Outputs | Error Behavior | Code Location | Status | Source Requirement |
|---|---|---|---|---|---|---|---|---|---|
| **1** | Phase 1 | GitHub Sign-In & OAuth Flow | OAuth 2.0 / GitHub App web flow for user authentication without manual PAT entry | OAuth authorization code | Session JWT / HttpOnly Cookie | 401 Unauthorized | `platform/server/routers/auth.py:15-25` (Currently only PAT login) | 🔴 Missing | `INSTRUCTIONS_TASKS.md:119-125` |
| **2** | Phase 1 | Secure Credential Storage | Encrypted storage of repository installation tokens, isolated per tenant | GitHub App Token / PAT | Encrypted ciphertext | Encryption failure raises 500 | `platform/server/services/auth_service.py:19-24`, `db.py:46` | 🟡 Partial (Plaintext in JWT) | `INSTRUCTIONS_TASKS.md:123`, `CONTEXT.md:37` |
| **3** | Phase 1 | Repository Authorization & Selection | Listing user repositories and authorizing SafeLane access | User Session Token | Accessible repo list | 400 Bad Request on GitHub API error | `platform/server/routers/github_setup.py:18-36` | 🟡 Partial (Uses PAT from JWT) | `INSTRUCTIONS_TASKS.md:121-124` |
| **4** | Phase 1 | Permission Review & Revocation | View, modify, or revoke active repository connections | Registration ID | Updated status / 200 OK | 404 Not Found if missing | `platform/server/routers/registrations.py:20-70` | 🟡 Partial (Soft delete only) | `INSTRUCTIONS_TASKS.md:124` |
| **5** | Phase 2 | Webhook Ingestion & HMAC Verification | Receive and verify GitHub webhook PR events with HMAC SHA-256 | Request Body, `X-Hub-Signature-256`, `X-GitHub-Event` | 202 Accepted | 401 Unauthorized on missing/invalid signature | `safelane/adapters/github.py:39-114` | 🟡 Partial (Workflow omits signature) | `INSTRUCTIONS_TASKS.md:129`, `github.py:48` |
| **6** | Phase 2 | PR Details & Diff Extraction | Fetch PR diff and list of changed files from GitHub API | PR Number, Repo Name | `PRPayload(diff, changed_files)` | 500 / `INSUFFICIENT_ANALYSIS` on API error | `safelane/adapters/github.py:80-111` | 🟡 Partial (Silent empty fallback) | `INSTRUCTIONS_TASKS.md:128` |
| **7** | Phase 2 | Full Entity Sync (Branches, Commits, Workflows) | Synchronize branches, commits, PRs, reviews, and workflow status | Repo Name, Webhook/Cron | Synchronized DB records | Sync error logged in DB | Missing (No branch/commit/review sync) | 🔴 Missing | `INSTRUCTIONS_TASKS.md:128` |
| **8** | Phase 2 | Scheduled Background Drift Sync | Background periodic job to sync repo state and detect drift | Cron interval / Lifespan task | Sync status & timestamps | Sync errors stored in DB | Missing (Only webhook trigger exists) | 🔴 Missing | `INSTRUCTIONS_TASKS.md:130-131` |
| **9** | Phase 2 | Orchestrator Agent Concurrency & Budgets | Concurrently dispatch 4 evidence modules with timeouts and token budgets | `PRPayload`, `RepoContext` | `VerdictReport` | Timed out module returns warning fallback | `safelane/fabric/controller.py:87-131` | 🟡 Partial (Basic `gather` without token budget) | `safelane/fabric/controller.py:87` |
| **10**| Phase 2 | Change Intelligence Diff Analysis | Heuristic & LLM analysis of code diffs for error handling, retries, and schema drops | `PRPayload`, Diff | `EvidenceResult(change_intelligence)` | Falls back to heuristics on LLM failure | `safelane/evidence/change_intelligence.py:49-130` | 🟢 Implemented | `change_intelligence.py` |
| **11**| Phase 2 | Incident Memory Retrieval | Query semantic vector index for historical incidents matching changed files | `PRPayload`, Changed Files | `EvidenceResult(incident_memory)` | Returns pass/warning if index unavailable | `safelane/evidence/incident_memory.py:33-97` | 🟡 Partial (Uses Azure Search / mock) | `incident_memory.py` |
| **12**| Phase 2 | Verification Readiness Check | Inspect repository test files for changed modules via GitHub API | `PRPayload`, Changed Files | `EvidenceResult(verification_readiness)` | Returns warning on API failure | `safelane/evidence/verification_readiness.py:10-112` | 🟢 Implemented | `verification_readiness.py` |
| **13**| Phase 2 | Release Context Evaluation | Calendar & holiday heuristic evaluation of deployment timing | `PRPayload`, Timestamp | `EvidenceResult(release_context)` | Defaults to current UTC timestamp | `safelane/evidence/release_context.py:55-110` | 🟢 Implemented | `release_context.py` |
| **14**| Phase 3 | Output Schema & Quality Evaluation | Validate agent reasoning, relevance, groundedness, and token budgets | Agent output | Validation Verdict / Retry Feedback | Retries bounded to 2 iterations | `safelane/adapters/foundry.py:102-105` (stubbed `return None`) | 🔴 Missing | `INSTRUCTIONS_TASKS.md:102-104` |
| **15**| Phase 3 | Dashboard UI & Analytics APIs | Repository cards, safety scores, safe/warning/blocked status, open PRs | HTTP Requests | JSON stats / React Dashboard | 500 on server error | Missing (`frontend/index.html` has no dashboard) | 🔴 Missing | `INSTRUCTIONS_TASKS.md:133-142` |
| **16**| Phase 4 | Deterministic Security Preflight | Static regex scanner for secrets, CI/CD risks, code execution, SSL, prompt injection | Diff, PR Title, Body | `list[SecurityFinding]` | Scanner exception yields warning finding | `safelane/fabric/security_preflight.py:56-137` | 🟢 Implemented | `security_preflight.py` |
| **17**| Phase 4 | Canonical Policy & Verdict Engine | Single authoritative calculation of confidence score (0-100) and decision | `EvidenceResult` list, `SecurityFinding` list | `VerdictReport` | Invariant violation raises ValueError | `safelane/fabric/verdict.py:6-90`, `controller.py:15-82` | 🟡 Partial (Duplicate conflicting logic in controller) | `verdict.py` |
| **18**| Phase 4 | Fixed-Template GitHub Publisher | Post markdown report and `@copilot` test generation nudges to GitHub PR | `VerdictReport`, Repo, PR, Token | Boolean success | Retries 3 times with exponential backoff | `safelane/fabric/publisher.py:17-115` | 🟢 Implemented | `publisher.py` |
| **19**| Phase 4 | Repository Workspace UI | Detailed view for branches, PRs, findings breakdown, affected files, recommendations | Repo Full Name | Workspace View | 404 Not Found | Missing | 🔴 Missing | `INSTRUCTIONS_TASKS.md:143-149` |
| **20**| Phase 5 | PostgreSQL Relational Schema & Migrations | Durable schema for users, repos, PRs, analyses, findings, verdicts, events | DB Connection | SQL Tables / Models | Connection error raises exception | `platform/server/services/db.py:30-55` (Only 2 basic tables, no migrations) | 🟡 Partial | `INSTRUCTIONS_TASKS.md:111-113` |
| **21**| Phase 5 | Qdrant Semantic Incident Memory Store | Embeddings generation and vector search for incident memory | Incident texts, changed files | Relevant incident vectors | Degrades safely to no-result | Missing (Currently Azure Search / mock in `incident_store.py`) | 🔴 Missing | `INSTRUCTIONS_TASKS.md:114-116` |
| **22**| Phase 5 | Activity Timeline & In-App Notifications | Event timeline for PRs, reviews, workflows, verdicts; notifications for blocked PRs | Event streams | Timeline JSON / Notification UI | 400 Bad Request | Missing | 🔴 Missing | `INSTRUCTIONS_TASKS.md:150-154` |
| **23**| Phase 5 | Live OpenTelemetry Tracing | Distributed tracing across orchestration, agent calls, and database operations | Active Spans | OTLP / Application Insights | Silent no-op if unconfigured | `safelane/adapters/foundry.py:21-56` (Helpers exist but disconnected) | 🟡 Partial (Disconnected from `controller.py`) | `safelane/adapters/foundry.py` |
| **24**| Phase 6 | Long-Term Analytics & Reporting | Safety score trends, recurring risks, incident frequency, weekly/monthly reports | Repo History | Aggregate metrics / charts | Empty dataset if no history | Missing | 🔴 Missing | `INSTRUCTIONS_TASKS.md:155-162` |
| **25**| Phase 6 | Developer CLI & Local Preflight | Local command-line tool to run SafeLane preflight checks on uncommitted diffs | Local git diff | Console summary & exit code | Non-zero exit code on critical findings | Missing | 🔴 Missing | `MASTER_PROMPT.md:12-25` |
| **26**| Phase 7 | Branch / Commit Graph Visualization | Interactive visual graph linking commits -> files -> PR -> findings | Repo metadata | SVG / Canvas Graph UI | Error placeholder on load failure | Missing | 🔴 Missing | `INSTRUCTIONS_TASKS.md:163-167` |
| **27**| Phase 7 | Production Security Hardening & Rate Limiting | Restrict CORS, secure cookies, CSRF protection, API rate limiting, tenant isolation | HTTP Requests | Protected responses | 429 Too Many Requests / 403 Forbidden | `platform/server/app.py:22-28` (Currently wildcard CORS `*`) | 🔴 Missing (Insecure CORS) | `INSTRUCTIONS_TASKS.md:182` |

---

### 2.2 Confirmed 22-Problem Ledger & Root Cause Mapping

| # | Severity | Issue Summary | Exact Code Location | Root Cause & Production Impact |
|---|---|---|---|---|
| **1** | **Critical** | Orchestrator ignores DB registrations | `safelane/adapters/github.py:16-26` | `get_repo_context()` reads `GITHUB_TOKEN` from env instead of querying `Registration` table in `db.py`. Analysis fails or uses wrong credentials for registered repos in multi-tenant environments. |
| **2** | **Critical** | Webhook HMAC verification fails on workflow triggers | `platform/server/services/github_service.py:25` vs `safelane/adapters/github.py:48-55` | `safelane-gate.yml` template curls webhook without calculating or sending `X-Hub-Signature-256`. Webhook rejects requests with 401 when `GITHUB_WEBHOOK_SECRET` is set. |
| **3** | **High** | README references non-existent server path | `README.md:102` | Mentions `uvicorn agents.orchestrator.server:app` which causes immediate startup crash. Actual server entry point is `safelane.adapters.github:app` or `platform.server.app:app`. |
| **4** | **High** | GitHub fetch failures lead to empty analysis | `safelane/adapters/github.py:100-102` | Catches exceptions during PR diff/files fetch, logs error, and proceeds with `diff=""` and `changed_files=[]` instead of failing fast or marking `INSUFFICIENT_ANALYSIS`. |
| **5** | **High** | Azure incident-ingestion functions are stubbed | `function_deploy/function_app.py:21, 28, 44` | Timer and EventGrid triggers contain only `pass` statements; no actual log querying or indexing logic is implemented. |
| **6** | **High** | Incident uploader and reader schemas mismatch | `mcp_servers/azure_mcp_server/sample_data.py:8-48` vs `safelane/evidence/incident_store.py:8-15, 69-76` | Uploader uses `incident_id`, `description`, `affected_repo`. Reader expects `id`, `summary`, `affected_files`. Queries fail to populate incident fields. |
| **7** | **High** | Foundry tracing helpers disconnected from live path | `safelane/adapters/foundry.py:33-56` | `trace_orchestrate` and `trace_agent_call` are defined but never imported or invoked in `safelane/fabric/controller.py`. Cloud tracing is completely silent. |
| **8** | **High** | Plaintext PAT exposed in browser JWT | `platform/server/routers/auth.py:21` | JWT payload stores `"pat": req.pat` unencrypted. Any client-side token inspection exposes the user's GitHub Personal Access Token. |
| **9** | **High** | Duplicate and inconsistent verdict logic | `safelane/fabric/controller.py:15-82` vs `safelane/fabric/verdict.py:6-90` | `controller.py` defines its own `build_verdict()` with `<60` threshold and raw modifier addition, bypassing `verdict.py`'s weighted scoring (`MODULE_WEIGHTS`) and `<70` threshold. Causes Pydantic `ValueError` crashes on scores between 60 and 69. |
| **10**| **High** | Tests emphasize mock paths over live pipeline | `tests/integration/test_v2_fabric.py:39-66` | Integration tests monkeypatch evidence modules with simple lambda mocks rather than testing realistic data flows. |
| **11**| **Medium** | Missing dependencies in audit runtime | `requirements.txt:10` | `openai` was previously missing (now listed in `requirements.txt:10`, but runtime environments need lockfile verification). |
| **12**| **Medium** | Broader dependency set than required | `requirements.txt:11-25` | Includes unused packages (`aiohttp`, `msal`, multiple Azure SDKs) while missing Qdrant or lightweight alternatives. |
| **13**| **Medium** | Permissive CORS configuration | `platform/server/app.py:24` | `allow_origins=["*"]` allows any third-party origin to make authenticated requests with credentials. |
| **14**| **Medium** | No production migration mechanism | `platform/server/services/db.py:56-59` | Relies on `Base.metadata.create_all`. Schema changes cannot be applied incrementally in production without data loss. |
| **15**| **Medium** | Missing relational constraints on User/Registration | `platform/server/services/db.py:43-45` | `Registration.user_id` is an unindexed integer with no ForeignKey constraint to `User.id`, and no unique constraint on `(user_id, owner, repo)`. |
| **16**| **Medium** | Azure Search config not passed to incident analysis | `safelane/adapters/github.py:16-26` | Mock `RepoContext` only sets `gh_token`, leaving `azure_search_endpoint` and `azure_search_key` as `None`. Incident memory always falls back to "No deployment connection". |
| **17**| **Medium** | Dead configuration variables | `.env.example:35` | `SAFELANE_FREE_TIER_LIMIT` is documented but never referenced or enforced anywhere in the code. |
| **18**| **Medium** | Disconnected Foundry quality evaluators | `safelane/adapters/foundry.py:102-105` | `evaluate_quality()` returns `None` unconditionally. |
| **19**| **Medium** | MCP directory is scaffolding only | `mcp_servers/azure_mcp_server/sample_data.py` | No MCP server protocol implementation or standard JSON-RPC endpoints exist. |
| **20**| **Medium** | Azure Function ingestion is scaffolding | `function_deploy/function_app.py` | Entire directory is isolated scaffolding with no integration into SafeLane orchestrator. |
| **21**| **Medium** | Stale "Prism" legacy references | `README.md:104, 128` | Documentation references old project name `prism` and `.github/workflows/prism-gate.yml`. |
| **22**| **Medium** | Duplicate verdict implementations | `safelane/fabric/controller.py:15` | Same as issue #9; needs consolidation into `safelane/fabric/verdict.py`. |

---

### 2.3 Edge Cases & Failure Modes Analysis

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Input Scenario                    │ Current Behavior            │ Target Production Behavior    │
├───────────────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ Null bytes in diff: "a\x00b"      │ inputs.py strips \x00       │ Sanitized safely via NFKC     │
│ Oversized diff (>200k chars)      │ inputs.py truncates to 200k │ Truncated + finding logged    │
│ Empty or whitespace-only diff     │ change_intel adds 20 risk   │ Flags INSUFFICIENT_ANALYSIS   │
│ Schema drop (DROP TABLE users;)   │ change_intel adds 60 risk   │ Critical finding + Hard Block │
│ LLM enrichment service fails      │ Falls back to regex rules   │ Deterministic fallback works  │
│ Qdrant service offline / timeout  │ Falls back to "no history"  │ Safe warning fallback (mod +10│
│ ≥2 Evidence modules fail/timeout  │ Drops score by only 15-30   │ Halts as INSUFFICIENT_ANALYSIS│
│ Change Intelligence module fails  │ Continues with blind score  │ Halts as INSUFFICIENT_ANALYSIS│
│ Stale webhook event (out-of-order)│ Overwrites newer commit SHA │ Discards via OCC head_sha chk │
│ PR deletes test suite (test_*.py) │ verification adds 60 risk   │ Critical finding + Hard Block │
│ Deploy on Christmas / Friday 5pm  │ release adds 20-35 risk     │ Flags release timing advisory │
│ Hardcoded AWS / Private Key       │ preflight adds 25 (capped)  │ Critical finding + Redacted   │
│ Prompt Injection in PR Title/Body │ preflight flags warning     │ Stripped from agent context   │
│ Score < 70 with 0 critical errors │ controller sets "greenlight"│ BLOCKED state enforced strictly│
│                                   │ Pydantic crashes with error │                               │
│ Webhook secret missing in request │ Rejects with 401            │ Rejects with 401 Unauthorized │
└───────────────────────────────────┴─────────────────────────────┴───────────────────────────────┘
```

---

## 3. Industry Standards & Open-Source Benchmark Comparisons

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   BENCHMARK COMPARISON MATRIX                                   │
├───────────────────────┬─────────────────────────────┬───────────────────────────────────────────┤
│ Dimension             │ SafeLane v2 Current State   │ Industry Production Standard              │
├───────────────────────┼─────────────────────────────┼───────────────────────────────────────────┤
│ Guardrail Pipeline    │ Regex Preflight + Evidence  │ Guardrails AI / NeMo Guardrails:          │
│ Architecture          │ Heuristics + Inline Verdict │ Three-Tier Validation Rails (Input Rail → │
│                       │ (ad-hoc pipeline)           │ Execution Rail → Output/Policy Rail) with │
│                       │                             │ programmatic ValidationResult schemas     │
├───────────────────────┼─────────────────────────────┼───────────────────────────────────────────┤
│ LLM Interaction &     │ Raw OpenAI client calls     │ LiteLLM / Instructor / Pydantic v2:       │
│ Structured Outputs    │ without strict JSON schema  │ Typed schema validation (`response_format`│
│                       │ or token/rate budgets       │ with JSON schema), token accounting,      │
│                       │                             │ latency budgets, and fallback chains      │
├───────────────────────┼─────────────────────────────┼───────────────────────────────────────────┤
│ Control & Evaluation  │ No evaluator agent; simple  │ Bounded iterative self-correction loop    │
│ Layer                 │ exception fallback to       │ with Critic/Evaluator agent (max 2        │
│                       │ static warning              │ retries), token budget, and explicit      │
│                       │                             │ INSUFFICIENT_ANALYSIS terminal state      │
├───────────────────────┼─────────────────────────────┼───────────────────────────────────────────┤
│ Incident Vector       │ Azure AI Search lexical     │ Qdrant Vector Store: Dense embeddings     │
│ Retrieval             │ string match + mock data    │ (FastEmbed/OpenAI), cosine similarity,    │
│                       │                             │ payload filtering on repo/files/severity  │
├───────────────────────┼─────────────────────────────┼───────────────────────────────────────────┤
│ Backend API & Service │ Split-brain: 2 FastAPI apps │ Unified Modular FastAPI Application:      │
│ Architecture          │ (:8000 Fabric, :8080 Setup) │ Single service with APIRouters, FastAPI   │
│                       │ with isolated state & CORS  │ `Depends` injection, BackgroundTasks/Celery│
├───────────────────────┼─────────────────────────────┼───────────────────────────────────────────┤
│ Database & State      │ SQLite/PostgreSQL with      │ PostgreSQL 16 + AsyncPG connection pool,  │
│ Persistence           │ `Base.metadata.create_all`  │ Alembic versioned migrations, fully       │
│                       │ and 2 simple tables         │ normalized relational schema (Phases 1-7) │
├───────────────────────┼─────────────────────────────┼───────────────────────────────────────────┤
│ Authentication &      │ User-supplied PAT in plain  │ GitHub App installation tokens (short-    │
│ GitHub Access         │ JWT; global server token    │ lived 1h) + GitHub OAuth 2.0 PKCE,        │
│                       │                             │ backend-only encrypted secrets storage    │
├───────────────────────┼─────────────────────────────┼───────────────────────────────────────────┤
│ Observability &       │ Disconnected helper methods │ OpenTelemetry Distributed Tracing, OTLP   │
│ Telemetry             │ in unused module            │ export to Prometheus/Azure Monitor/Jaeger,│
│                       │                             │ Prometheus metrics endpoint, span context │
└───────────────────────┴─────────────────────────────┴───────────────────────────────────────────┘
```

### 3.1 Guardrails AI & NeMo Guardrails (Three-Tier Validation Rails)

In enterprise AI safety, modern guardrails implement a three-tier validation rail:
1. **Input Rail (Ingestion & Sanitization)**:
   - Untrusted repository content (diffs, commit messages, PR descriptions, issue comments) contains adversarial inputs or formatting anomalies.
   - Guardrails pattern: Apply NFKC unicode normalization, strip binary control characters, enforce strict character caps (200,000 characters for diffs, 1,024 characters for file paths), and execute static regex filters for prompt injection phrases (`"ignore previous instructions"`, `"system promptoverride"`).
2. **Execution Rail (Parallel Evidence Gathering with Budgets)**:
   - Concurrently invoke specialized evidence modules using `asyncio.gather()` or `asyncio.TaskGroup()`.
   - Each module runs within an isolated timeout (e.g. 15s for Change Intel, 5s for Qdrant, 10s for Verification Readiness) and token budget. If an agent fails or exhausts its budget, it produces a typed `ValidationResult` with status `warning` rather than throwing uncaught exceptions.
3. **Output & Policy Rail (Deterministic Gating)**:
   - AI generated text is strictly decoupled from the verdict outcome.
   - The Policy Rail consumes typed evidence objects and executes deterministic math: computing confidence scores (0–100), enforcing hard blocking rules for secrets/critical vulnerabilities, and generating reproducible rollback playbooks.

### 3.2 LiteLLM, Instructor & Pydantic v2 (Structured Schema & Token Budgets)

1. **Strict JSON Schema Enforcement**:
   - Rather than unstructured markdown parsing, all LLM calls use structured outputs (`response_format={"type": "json_object"}` or OpenAI function calling / Instructor / Pydantic schema validation).
2. **Token Accounting & Budgets**:
   - Every LLM invocation records `prompt_tokens`, `completion_tokens`, and `latency_ms`.
   - Hard upper bounds (e.g. max 4,000 prompt tokens per PR diff chunk) prevent denial-of-wallet attacks and context exhaustion.
3. **Fallback Chains**:
   - Primary: Azure AI Foundry / OpenAI GPT-4o structured completion.
   - Fallback: Local deterministic regex heuristics (zero external dependencies).

### 3.3 FastAPI Production Standards (Unified Modular Application)

1. **APIRouter Domain Organization**:
   - Modular routing structure under `/api/v1/`: `auth`, `github`, `registrations`, `dashboard`, `workspace`, `timeline`, `notifications`, `analytics`, and `webhooks`.
2. **FastAPI Dependency Injection (`Depends`)**:
   - Centralized dependency injection for database sessions (`get_db_session`), authenticated user context (`get_current_user`), and encryption services.
3. **Async Lifespan Context Manager**:
   - Modern FastAPI `lifespan` handler initializing database connection pools, Qdrant client connections, and background sync worker tasks.

### 3.4 PostgreSQL 16 + AsyncPG Connection Pooling

1. **Asynchronous Connection Pooling**:
   - Use `create_async_engine("postgresql+asyncpg://...")` with pool sizing: `pool_size=20`, `max_overflow=10`, `pool_timeout=30`, `pool_recycle=1800`.
2. **Schema Versioning via Alembic**:
   - Discard `Base.metadata.create_all()` in production.
   - All schema changes versioned via linear Alembic migration scripts (`alembic upgrade head`).

### 3.5 Qdrant Vector Database (Incident Semantic Retrieval)

1. **Dense Vector Embeddings**:
   - Text representation generated via OpenAI `text-embedding-3-small` (1536-dim) or FastEmbed `BAAI/bge-small-en-v1.5` (384-dim).
2. **Payload Indexing & Filtering**:
   - Payload indexes on `repository` (keyword), `affected_files` (keyword array), and `severity` (keyword).
   - Filtered semantic search ensuring tenant isolation across repositories.

### 3.6 OpenTelemetry & W3C Distributed Tracing

1. **W3C TraceContext Propagation**:
   - Extract incoming `traceparent` headers from GitHub webhooks or developer requests.
2. **OTel Semantic Conventions**:
   - Trace HTTP requests, database transactions, vector queries, LLM calls, and verdict calculations with standard semantic attributes (`db.system`, `gen_ai.request.model`, `http.status_code`).

---

## 4. Phase-by-Phase Comprehensive Technical Specifications

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PHASE EXECUTION ROADMAP                                        │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Phase 1: Core Architecture, GitHub Identity & Ingestion (OAuth, App Tokens, Unified Server)      │
│ Phase 2: Execution Engine, Entity Synchronization & Multi-LLM Routing (HMAC Webhook, Budgets)   │
│ Phase 3: Control & Evaluation Suite, Verification Logic & Dashboard API / UI                     │
│ Phase 4: Authoritative Policy Engine, Security Preflight & Repository Workspace                  │
│ Phase 5: Durable Persistence (PostgreSQL + Alembic), Qdrant Vector Store & Unified Timeline     │
│ Phase 6: Developer Experience, CLI Tool (`safelane check`) & Long-Term Analytics Engine          │
│ Phase 7: Production Hardening (CORS, CSRF, Rate Limiting), Commit Graph & Benchmarking           │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 4.1 Phase 1: Core Architecture, GitHub Identity & Ingestion

#### 1. Objectives & Scope
- Eliminate the insecure manual Personal Access Token (PAT) input flow.
- Implement GitHub OAuth 2.0 Web Application Flow and GitHub App Installation token management.
- Ensure all sensitive tokens are encrypted at rest (AES-256-GCM / Fernet) and never sent to browser clients in JWT claims.
- Unify the split-server architecture into a single FastAPI service.

#### 2. Current State vs. Gaps
- **Current State**:
  - `platform/server/routers/auth.py:15-25`: `POST /api/auth/token` accepts raw PAT, stores `"pat": req.pat` in unencrypted JWT payload.
  - `platform/server/routers/github_setup.py`: Reads PAT from decoded JWT.
  - `safelane/adapters/github.py`: Uses `os.environ["GITHUB_TOKEN"]` and mock registration ID.
- **Identified Gaps**:
  - Severe credential leakage in browser JWT.
  - No OAuth 2.0 PKCE / GitHub App authentication flow.
  - Dual server processes (`:8000` Fabric vs `:8080` Platform).

#### 3. Detailed Technical Specifications

##### API Endpoints:
```http
POST /api/v1/auth/github/login
Summary: Initiate GitHub OAuth 2.0 login flow
Response 200: {"authorization_url": "https://github.com/login/oauth/authorize?client_id=...&scope=read:user,repo&state=..."}

GET /api/v1/auth/github/callback?code={code}&state={state}
Summary: Exchange OAuth code for GitHub user access token, create/update User record, issue HttpOnly JWT session cookie
Response 302: Redirect to /dashboard (Set-Cookie: safelane_session=...; HttpOnly; Secure; SameSite=Lax; Max-Age=86400)

GET /api/v1/auth/me
Summary: Get current authenticated user details
Headers: Cookie: safelane_session=...
Response 200: {
  "id": 1,
  "github_id": 1234567,
  "username": "octocat",
  "email": "octocat@github.com",
  "avatar_url": "https://avatars.githubusercontent.com/u/1234567"
}

POST /api/v1/auth/logout
Summary: Invalidate session cookie
Response 200: {"status": "logged_out"}
```

##### Token Encryption & Decryption Service:
```python
# safelane/services/crypto.py
from cryptography.fernet import Fernet
import os

class EncryptionService:
    def __init__(self, key: str | None = None):
        self._key = key or os.environ["ENCRYPTION_KEY"]
        self._cipher = Fernet(self._key.encode() if isinstance(self._key, str) else self._key)

    def encrypt(self, raw_token: str) -> str:
        if not raw_token:
            return ""
        return self._cipher.encrypt(raw_token.encode()).decode()

    def decrypt(self, encrypted_token: str) -> str:
        if not encrypted_token:
            return ""
        return self._cipher.decrypt(encrypted_token.encode()).decode()
```

##### GitHub App Dynamic Token Minting Architecture:
```python
# safelane/services/github_app_auth.py
import time
import httpx
import jwt
from datetime import datetime, timezone
from safelane.services.crypto import EncryptionService

class InstallationTokenManager:
    """
    Manages GitHub App installation access tokens dynamically.
    Mints short-lived (1-hour TTL) installation tokens using RS256 JWTs signed with 
    the GitHub App Private Key and refreshes automatically when remaining TTL < 5 minutes.
    """
    def __init__(
        self,
        app_id: str,
        private_key_pem: str,
        encryption_service: EncryptionService | None = None
    ):
        self.app_id = app_id
        self.private_key_pem = private_key_pem
        self.encryption_service = encryption_service or EncryptionService()
        self._token_cache: dict[int, tuple[str, float]] = {}  # installation_id -> (token, expire_epoch)

    def _generate_app_jwt(self) -> str:
        now = int(time.time())
        payload = {
            "iat": now - 60,       # 60s in the past to account for clock drift
            "exp": now + (10 * 60), # GitHub maximum JWT lifetime is 10 minutes
            "iss": self.app_id
        }
        return jwt.encode(payload, self.private_key_pem, algorithm="RS256")

    async def get_installation_token(self, installation_id: int) -> str:
        now = time.time()
        # Check cache: reuse if valid for at least 5 more minutes (300 seconds)
        if installation_id in self._token_cache:
            token, expires_at = self._token_cache[installation_id]
            if expires_at - now > 300:
                return token

        # Mint new installation access token via GitHub App JWT
        app_jwt = self._generate_app_jwt()
        url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        token = data["token"]
        expires_at_iso = data["expires_at"]
        expires_epoch = datetime.fromisoformat(expires_at_iso.replace("Z", "+00:00")).timestamp()
        
        self._token_cache[installation_id] = (token, expires_epoch)
        return token
```

#### 4. Step-by-Step Implementation Backlog
1. Consolidate `platform/server/app.py` and `safelane/adapters/github.py` into `safelane/server/app.py`.
2. Implement `EncryptionService` in `safelane/services/crypto.py` and `InstallationTokenManager` in `safelane/services/github_app_auth.py`.
3. Create `safelane/server/routers/auth.py` with GitHub OAuth 2.0 authorization code exchange and HttpOnly session cookies.
4. Update `RepoContext` resolution in `safelane/adapters/github.py` to use `InstallationTokenManager` for dynamic 1h token minting and PostgreSQL token resolution.
5. Purge plaintext PAT fields from all JWT tokens and frontend localStorage.

---

### 4.2 Phase 2: Execution Engine, Synchronization & Multi-LLM Routing

#### 1. Objectives & Scope
- Receive GitHub webhook events (`pull_request`, `push`, `workflow_run`) with native HMAC-SHA256 signature verification.
- Provide reliable PR diff, commit history, and changed file extraction with comprehensive error handling.
- Dispatch the 4 evidence modules concurrently with timeouts, token budgets, and LLM fallback routing.
- Implement background periodic entity synchronization to detect drift.

#### 2. Current State vs. Gaps
- **Current State**:
  - `safelane/fabric/controller.py`: `asyncio.gather` with 30s timeout, but lacks token budget tracking and evaluation retries.
  - `platform/server/services/github_service.py`: Generates workflow running `curl` without `X-Hub-Signature-256`.
  - `safelane/adapters/github.py:100`: Catches diff fetch errors and silently proceeds with empty diff.
- **Identified Gaps**:
  - Webhook 401 signature errors when secret is active.
  - No background drift synchronization.
  - Silent failure on diff fetch.

#### 3. Detailed Technical Specifications

##### Native GitHub Webhook Handler:
```http
POST /webhook/github
Headers:
  X-GitHub-Event: pull_request
  X-Hub-Signature-256: sha256=d57c29...
  X-GitHub-Delivery: 72d3162e-cc78-11e3-81ab-4c9367dc0958
Payload: { "action": "opened", "pull_request": { "number": 42, ... }, "repository": { "full_name": "org/repo" } }
Response 202 Accepted: {"status": "queued", "delivery_id": "72d3162e-cc78-11e3-81ab-4c9367dc0958"}
```

##### Concurrency & Execution Control Algorithm:
```python
# safelane/fabric/orchestrator.py
import asyncio
import logging
from safelane.contracts import PRPayload, RepoContext, EvidenceResult, VerdictReport
from safelane.fabric.security_preflight import run_security_preflight
from safelane.evidence.change_intelligence import analyze_change_intelligence
from safelane.evidence.incident_memory import retrieve_incident_memory
from safelane.evidence.verification_readiness import evaluate_verification_readiness
from safelane.evidence.release_context import evaluate_release_context
from safelane.fabric.verdict import build_verdict

logger = logging.getLogger(__name__)

MODULE_TIMEOUT_SECONDS = 20.0

async def _run_module_bounded(mod_name: str, coro, timeout: float = MODULE_TIMEOUT_SECONDS) -> EvidenceResult:
    """Wraps each evidence module with strict timeout and standardized fallback degradation."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"Module '{mod_name}' timed out after {timeout}s.")
        # Standardized degradation: Qdrant modifier is 10, other modules use 15
        modifier = 10 if mod_name == "incident_memory" else 15
        return EvidenceResult(
            module=mod_name,
            status="warning",
            risk_score_modifier=modifier,
            findings=[f"Analysis timed out after {timeout:.1f}s ({mod_name})."],
            recommended_action=f"Manual review required: {mod_name} evidence incomplete due to timeout."
        )
    except Exception as exc:
        logger.error(f"Module '{mod_name}' failed with unhandled exception: {exc}", exc_info=True)
        modifier = 10 if mod_name == "incident_memory" else 15
        return EvidenceResult(
            module=mod_name,
            status="warning",
            risk_score_modifier=modifier,
            findings=[f"Module error ({mod_name}): {str(exc)}"],
            recommended_action=f"Manual verification required due to module execution error ({mod_name})."
        )

async def orchestrate_analysis(
    payload: PRPayload,
    context: RepoContext,
    current_head_sha: str | None = None
) -> VerdictReport:
    # 1. Optimistic Concurrency Control Check: verify commit SHA is not superseded
    if current_head_sha and payload.commit_sha != current_head_sha:
        logger.info(f"Superseded analysis aborted: commit {payload.commit_sha} != latest HEAD {current_head_sha}")
        raise asyncio.CancelledError(f"Superseded by newer commit {current_head_sha}")

    # 2. Deterministic Security Preflight (Fast, Synchronous)
    security_findings = run_security_preflight(payload.diff, payload.title, payload.body)
    
    # 3. Parallel Evidence Module Dispatch (Strict Timeout Wrapping)
    tasks = [
        asyncio.create_task(_run_module_bounded("change_intelligence", analyze_change_intelligence(payload, context))),
        asyncio.create_task(_run_module_bounded("incident_memory", retrieve_incident_memory(payload, context))),
        asyncio.create_task(_run_module_bounded("verification_readiness", evaluate_verification_readiness(payload, context))),
        asyncio.create_task(_run_module_bounded("release_context", evaluate_release_context(payload, context))),
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=False)
    evidence_results: list[EvidenceResult] = list(results)
    
    # 4. Track Module Degradation & Failure Thresholds
    failed_modules = [
        r for r in evidence_results 
        if any("timed out" in f or "Module error" in f for f in r.findings)
    ]
    change_intel_failed = any(
        r.module == "change_intelligence" and any("timed out" in f or "Module error" in f for f in r.findings)
        for r in evidence_results
    )
    
    # 5. Canonical Authoritative Verdict Calculation
    # If >= 2 modules fail, or Change Intel fails, decide_policy() halts to INSUFFICIENT_ANALYSIS (score 0)
    verdict = build_verdict(
        payload,
        evidence_results,
        security_findings,
        failed_modules_count=len(failed_modules),
        change_intel_failed=change_intel_failed
    )
    return verdict
```

#### 4. Step-by-Step Implementation Backlog
1. Implement HMAC-SHA256 verification in `safelane/server/routers/webhooks.py` utilizing `hmac.compare_digest`.
2. Replace the `curl` workflow injection mechanism with native GitHub Webhook creation via GitHub API (`POST /repos/{owner}/{repo}/hooks`).
3. Add robust GitHub API diff fetcher in `safelane/adapters/github_client.py` raising typed `DiffFetchError` on 404/401/500 rather than returning empty diffs.
4. Implement background sync worker using APScheduler or FastAPI lifespan background loop updating repository entity metadata every 15 minutes.
5. Implement Optimistic Concurrency Control in webhook event processing: cancel in-flight analysis jobs when newer commits arrive for the same PR and verify `head_sha` before updating database records or posting GitHub check runs.

---

### 4.3 Phase 3: Control & Evaluation Suite, Verification Logic & Dashboard

#### 1. Objectives & Scope
- Build an automated Agent Control & Evaluation layer that verifies agent output schemas, factual grounding, and token limits.
- Implement a bounded feedback loop (max 2 retries) when evidence fails validation.
- Build Dashboard REST APIs and responsive UI displaying repository cards, safety scores, open PR counts, and safety trend charts.

#### 2. Current State vs. Gaps
- **Current State**:
  - `safelane/adapters/foundry.py:102-105`: `evaluate_quality()` is an empty stub returning `None`.
  - `platform/frontend/index.html`: Only contains a PAT input setup wizard.
- **Identified Gaps**:
  - Zero evaluation or retry mechanics.
  - Zero dashboard APIs or UI views.

#### 3. Detailed Technical Specifications

##### Evaluation & Quality Critic Engine:
```python
# safelane/fabric/evaluator.py
import re
from pydantic import BaseModel, Field
from safelane.contracts import EvidenceResult, PRPayload

class EvaluationVerdict(BaseModel):
    is_valid: bool
    grounded: bool
    retry_feedback: str | None = None
    token_usage_ok: bool = True

# Regex to detect relative and source code file paths (e.g. src/auth/jwt.py, config/db.json)
PATH_PATTERN = re.compile(r'\b(?:[a-zA-Z0-9_\-\.]+/)+[a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+\b')

def evaluate_evidence_quality(evidence: EvidenceResult, payload: PRPayload) -> EvaluationVerdict:
    # 1. Verify schema completeness based on module status
    # When status is "pass", findings may be empty and recommendations are optional.
    if evidence.status in ("warning", "critical"):
        if not evidence.findings:
            return EvaluationVerdict(
                is_valid=False,
                grounded=False,
                retry_feedback=f"Module '{evidence.module}' declared '{evidence.status}' status but provided no findings."
            )
        if not evidence.recommended_action:
            return EvaluationVerdict(
                is_valid=False,
                grounded=False,
                retry_feedback=f"Module '{evidence.module}' declared '{evidence.status}' status but omitted recommended action."
            )
    
    # 2. Check for hallucinated file paths by matching against payload.changed_files and diff
    changed_files_set = set(payload.changed_files or [])
    for finding in evidence.findings:
        # Extract candidate path tokens matching directory/file syntax
        candidate_paths = PATH_PATTERN.findall(finding)
        for path in candidate_paths:
            # Ignore web URLs, dates, or non-file tokens
            if path.startswith("http:") or path.startswith("https:") or "github.com" in path:
                continue
            
            # Verify candidate path is grounded in changed_files or verbatim in diff
            is_in_changed_files = (
                path in changed_files_set or 
                any(cf.endswith(path) or path.endswith(cf) for cf in changed_files_set)
            )
            is_in_diff = path in payload.diff
            
            if not is_in_changed_files and not is_in_diff:
                return EvaluationVerdict(
                    is_valid=False,
                    grounded=False,
                    retry_feedback=f"Referenced ungrounded file path '{path}' not present in PR changed files or diff."
                )
            
    return EvaluationVerdict(is_valid=True, grounded=True)
```

##### Dashboard REST API Endpoints:
```http
GET /api/v1/dashboard/summary
Summary: Overview statistics for logged-in user's repositories
Response 200: {
  "total_repositories": 12,
  "average_safety_score": 84.5,
  "active_blockers_count": 2,
  "recent_analyses_count": 48
}

GET /api/v1/dashboard/repositories?search={q}&status={safe|warning|blocked}&sort=score_asc
Summary: Paginated repository cards with current safety status
Response 200: {
  "items": [
    {
      "id": 101,
      "full_name": "acme/payment-gateway",
      "safety_score": 58,
      "status": "blocked",
      "open_prs_count": 3,
      "last_analysis_at": "2026-09-01T06:30:00Z",
      "critical_findings_count": 1
    }
  ],
  "total": 12,
  "page": 1,
  "page_size": 10
}
```

#### 4. Step-by-Step Implementation Backlog
1. Implement `safelane/fabric/evaluator.py` with schema and grounding validators.
2. Wire evaluator feedback into `safelane/fabric/orchestrator.py` with retry count tracking (max 2 iterations).
3. Create `safelane/server/routers/dashboard.py` with summary and repository list endpoints.
4. Develop React / Tailwind CSS Dashboard frontend with search, filters, safety badges, and historical score sparklines.

---

### 4.4 Phase 4: Authoritative Policy Engine, Security Preflight & Repository Workspace

#### 1. Objectives & Scope
- Consolidate all verdict calculation into a single canonical engine (`safelane/fabric/verdict.py`).
- Implement comprehensive deterministic Security Preflight scanning with strict redaction.
- Build Repository Workspace REST APIs and UI detailing branches, PRs, commit findings, and dynamic rollback playbooks.
- Retain constrained fixed-template PR commenting with `@copilot` test generation nudges.

#### 2. Current State vs. Gaps
- **Current State**:
  - `safelane/fabric/controller.py:15-82` contains a duplicate, conflicting `build_verdict()` with `<60` threshold that crashes Pydantic invariants.
  - `safelane/fabric/verdict.py` is complete but uncalled by `controller.py`.
  - No Workspace UI exists.
- **Identified Gaps**:
  - Duplicate verdict engine bug.
  - Missing Repository Workspace views.

#### 3. Detailed Technical Specifications

##### Canonical Verdict Calculation Specification:
```python
# safelane/fabric/verdict.py
MODULE_WEIGHTS = {
    "change_intelligence": 0.30,
    "incident_memory": 0.25,
    "verification_readiness": 0.25,
    "release_context": 0.20
}

def compute_evidence_score(evidence: list[EvidenceResult]) -> int:
    weighted_penalty = sum(
        r.risk_score_modifier * MODULE_WEIGHTS.get(r.module, 0.25)
        for r in evidence
    )
    return int(max(0, min(100, 100 - weighted_penalty)))

def decide_policy(
    base_score: int,
    evidence: list[EvidenceResult],
    security_findings: list[SecurityFinding],
    *,
    failed_modules_count: int = 0,
    change_intel_failed: bool = False,
    token_budget_exhausted: bool = False
) -> tuple[int, str]:
    # 1. Authoritative Failure Degradation & INSUFFICIENT_ANALYSIS Gating
    # If 2 or more modules fail/timeout, or if Change Intelligence fails, or token budget exhausted:
    if failed_modules_count >= 2 or change_intel_failed or token_budget_exhausted:
        return 0, "insufficient_analysis"

    # 2. Apply Deterministic Security Policy Penalties
    final_score, has_security_blocker = apply_security_policy(base_score, security_findings)
    
    has_critical_evidence = any(r.status == "critical" for r in evidence)
    has_warning_evidence = any(r.status == "warning" for r in evidence)
    
    # 3. Authoritative Decision Invariants
    if has_security_blocker or has_critical_evidence or final_score < 70:
        decision = "blocked"
    elif final_score >= 85 and not has_warning_evidence:
        decision = "greenlight"
    else:
        decision = "warning"
        
    return final_score, decision

def build_verdict(
    payload: PRPayload,
    evidence: list[EvidenceResult],
    security_findings: list[SecurityFinding],
    *,
    failed_modules_count: int = 0,
    change_intel_failed: bool = False,
    token_budget_exhausted: bool = False
) -> VerdictReport:
    base_score = compute_evidence_score(evidence)
    final_score, decision = decide_policy(
        base_score,
        evidence,
        security_findings,
        failed_modules_count=failed_modules_count,
        change_intel_failed=change_intel_failed,
        token_budget_exhausted=token_budget_exhausted
    )
    risk_brief = generate_risk_brief(decision, final_score, evidence, security_findings)
    rollback_playbook = generate_rollback_playbook(payload, security_findings, evidence) if decision == "blocked" else None
    
    return VerdictReport(
        confidence_score=final_score,
        decision=decision,
        risk_brief=risk_brief,
        rollback_playbook=rollback_playbook,
        evidence=evidence,
        security_findings=security_findings
    )
```

##### Repository Workspace REST API Endpoints:
```http
GET /api/v1/repositories/{id}/workspace
Summary: Comprehensive repository risk workspace
Response 200: {
  "repository": { "id": 101, "full_name": "acme/payment-gateway", "default_branch": "main" },
  "active_prs": [
    {
      "pr_number": 42,
      "title": "Drop legacy user auth columns",
      "author": "dev1",
      "head_sha": "a1b2c3d",
      "confidence_score": 45,
      "decision": "blocked",
      "security_findings_count": 1,
      "created_at": "2026-09-01T05:00:00Z"
    }
  ]
}

GET /api/v1/repositories/{id}/prs/{pr_number}/analysis
Summary: Detailed 4-agent evidence breakdown and rollback playbook for specific PR
Response 200: {
  "pr_number": 42,
  "confidence_score": 45,
  "decision": "blocked",
  "risk_brief": "### Risk Brief\n- Critical schema modification without backward compatibility.\n- Hardcoded API secret detected in diff.",
  "rollback_playbook": "### Rollback Playbook\n1. Run `git revert a1b2c3d`\n2. Execute database rollback migration: `alembic downgrade -1`\n3. Rotate exposed API credentials in secret vault.",
  "security_findings": [...],
  "evidence_results": [...]
}
```

#### 4. Step-by-Step Implementation Backlog
1. Delete inline `build_verdict()` from `safelane/fabric/controller.py` and import `safelane.fabric.verdict.build_verdict`.
2. Update `VerdictReport.decision` enum in `safelane/contracts.py` to support `Literal["greenlight", "warning", "blocked", "insufficient_analysis"]`.
3. Create `safelane/server/routers/workspace.py` with repository and PR analysis endpoints.
4. Implement Workspace UI view with line-level diff highlighting and expandable evidence accordions.

---

### 4.5 Phase 5: Durable Persistence, Qdrant Vector Memory & Unified Timeline

#### 1. Objectives & Scope
- Deploy normalized PostgreSQL schema for users, installations, repositories, PRs, analyses, findings, verdicts, events, and notifications.
- Implement Alembic versioned migration scripts.
- Replace legacy Azure AI Search with **Qdrant Vector Database** for semantic incident memory indexing and retrieval.
- Build the Unified Activity Timeline and In-App Notifications engine.
- Wire OpenTelemetry distributed tracing into the live orchestration pipeline.

#### 2. Current State vs. Gaps
- **Current State**:
  - `platform/server/services/db.py` contains only 2 minimal tables initialized via `create_all`.
  - `safelane/evidence/incident_memory.py` uses Azure AI Search / mock records.
  - `safelane/adapters/foundry.py` tracing is never called.
- **Identified Gaps**:
  - Missing 7 core domain tables and Alembic.
  - Zero Qdrant code in repository.
  - Missing timeline and notifications.
  - Disconnected tracing.

#### 3. Detailed Technical Specifications

##### Qdrant Semantic Incident Memory Client:
```python
# safelane/evidence/qdrant_incident_store.py
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import os

class QdrantIncidentStore:
    COLLECTION_NAME = "safelane_incidents"
    
    def __init__(self, url: str | None = None, api_key: str | None = None):
        self.client = AsyncQdrantClient(
            url=url or os.environ.get("QDRANT_URL", "http://localhost:6333"),
            api_key=api_key or os.environ.get("QDRANT_API_KEY")
        )

    async def init_collection(self, vector_size: int = 1536):
        collections = await self.client.get_collections()
        exists = any(c.name == self.COLLECTION_NAME for c in collections.collections)
        if not exists:
            await self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            # Create payload index for repository filtering
            await self.client.create_payload_index(
                collection_name=self.COLLECTION_NAME,
                field_name="repository",
                field_schema="keyword"
            )

    async def search_similar_incidents(
        self,
        query_vector: list[float],
        repository: str,
        limit: int = 3,
        score_threshold: float = 0.72
    ) -> list[dict]:
        repo_filter = Filter(
            must=[FieldCondition(key="repository", match=MatchValue(value=repository))]
        )
        try:
            points = await self.client.search(
                collection_name=self.COLLECTION_NAME,
                query_vector=query_vector,
                query_filter=repo_filter,
                limit=limit,
                score_threshold=score_threshold
            )
            return [p.payload for p in points if p.payload]
        except Exception:
            # Fallback handled upstream by orchestrator/incident_memory with standardized +10 warning
            return []
```

##### Activity Timeline REST API:
```http
GET /api/v1/repositories/{id}/timeline?limit=50
Summary: Chronological event stream of PRs, analyses, findings, and sync events
Response 200: {
  "events": [
    {
      "id": 501,
      "event_type": "analysis_completed",
      "timestamp": "2026-09-01T06:30:15Z",
      "title": "PR #42 Analysis Completed: BLOCKED",
      "severity": "critical",
      "metadata": { "pr_number": 42, "score": 45, "decision": "blocked" }
    }
  ]
}

GET /api/v1/notifications?unread_only=true
Summary: In-app user notifications for blocked PRs and critical alerts
Response 200: {
  "unread_count": 1,
  "notifications": [
    {
      "id": 1,
      "repo_full_name": "acme/payment-gateway",
      "title": "PR #42 Blocked by SafeLane",
      "message": "Critical security finding: Exposed AWS Secret Key.",
      "is_read": false,
      "created_at": "2026-09-01T06:30:15Z"
    }
  ]
}
```

#### 4. Step-by-Step Implementation Backlog
1. Initialize Alembic environment in `migrations/` and generate migration `001_initial_schema.py`.
2. Implement `QdrantIncidentStore` in `safelane/evidence/qdrant_incident_store.py` and update `incident_memory.py` to query Qdrant.
3. Build `safelane/server/routers/timeline.py` and `safelane/server/routers/notifications.py`.
4. Wrap `orchestrate_analysis()` with active OpenTelemetry span context tracing in `safelane/fabric/orchestrator.py`.

---

### 4.6 Phase 6: Developer Experience, CLI & Long-Term Analytics

#### 1. Objectives & Scope
- Develop a standalone SafeLane developer CLI (`safelane check`) allowing developers to run preflight and change intelligence on local uncommitted git diffs.
- Implement Long-Term Analytics services tracking historical safety trends, recurring risk categories, and verification test debt.
- Provide clean Python SDK bindings for programmatic analysis.

#### 2. Current State vs. Gaps
- **Current State**: Zero CLI tooling or analytics aggregation services exist.
- **Identified Gaps**: Complete absence of local DX and analytics reporting.

#### 3. Detailed Technical Specifications

##### SafeLane Developer CLI Architecture:
```python
# safelane/cli/main.py
import sys
import subprocess
import argparse
from safelane.fabric.security_preflight import run_security_preflight
from safelane.evidence.change_intelligence import scan_diff_heuristics

def run_local_preflight(target_branch: str = "main"):
    # 1. Extract git diff against target branch
    try:
        diff = subprocess.check_output(["git", "diff", f"{target_branch}...HEAD"], text=True)
    except subprocess.CalledProcessError:
        diff = subprocess.check_output(["git", "diff", "HEAD"], text=True)
        
    if not diff.strip():
        print("✅ No local changes detected.")
        sys.exit(0)
        
    print("🔍 Running SafeLane Local Preflight...")
    
    # 2. Run Deterministic Security Preflight
    findings = run_security_preflight(diff, "Local Preflight", "")
    has_critical = any(f.severity == "critical" for f in findings)
    
    for f in findings:
        icon = "🚨" if f.severity == "critical" else "⚠️"
        print(f"{icon} [{f.severity.upper()}] {f.rule_id} ({f.file_path}): {f.evidence}")
        print(f"   Fix: {f.remediation}\n")
        
    if has_critical:
        print("❌ Local Preflight FAILED: Critical security issues must be resolved before committing.")
        sys.exit(1)
    else:
        print("✅ Local Preflight PASSED: Code is ready for pull request.")
        sys.exit(0)
```

##### Long-Term Analytics API:
```http
GET /api/v1/analytics/repositories/{id}/trends?period=90d
Summary: Historical rolling safety score and risk category distributions
Response 200: {
  "period": "90d",
  "average_score": 88.2,
  "trend": "+4.5%",
  "score_history": [
    { "date": "2026-06-01", "average_score": 82 },
    { "date": "2026-07-01", "average_score": 86 },
    { "date": "2026-08-01", "average_score": 89 }
  ],
  "top_risk_categories": [
    { "category": "missing_tests", "occurrences": 14 },
    { "category": "weekend_deploy", "occurrences": 6 },
    { "category": "sql_drop", "occurrences": 2 }
  ]
}
```

#### 4. Step-by-Step Implementation Backlog
1. Implement `safelane/cli/main.py` and configure console script entrypoint `safelane = safelane.cli.main:main` in `pyproject.toml`.
2. Implement `safelane/server/routers/analytics.py` computing time-bucketed aggregations via SQL `date_trunc`.
3. Create Analytics UI dashboard displaying rolling score line charts and risk bar charts.

---

### 4.7 Phase 7: Production Hardening, Graph Visualization & Benchmarking

#### 1. Objectives & Scope
- Implement interactive Commit & Branch Graph visualizer showing where risk or incidents entered the commit tree.
- Apply strict production security hardening: restricted CORS whitelist, CSRF protection, secure HTTP-only session cookies, tenant isolation, and API rate limiting.
- Build automated benchmarking suite testing synthetic PR diffs and measuring throughput.

#### 2. Current State vs. Gaps
- **Current State**:
  - `platform/server/app.py:24`: Wildcard CORS `allow_origins=["*"]`.
  - `platform/server/services/db.py:14`: Insecure SSL bypass option.
  - Zero graph visualization or benchmarking suite.
- **Identified Gaps**: Insecure CORS, missing visualization and benchmarking.

#### 3. Detailed Technical Specifications

##### Production Security Middleware Configuration:
```python
# safelane/server/middleware.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

def configure_production_security(app: FastAPI):
    allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,https://safelane.io").split(",")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-GitHub-Event", "X-Hub-Signature-256"],
    )
```

##### Interactive Commit Graph REST API:
```http
GET /api/v1/repositories/{id}/graph?branch=main&limit=30
Summary: Directed Acyclic Graph (DAG) nodes and edges for commit tree with risk overlays
Response 200: {
  "nodes": [
    {
      "id": "a1b2c3d",
      "type": "commit",
      "author": "octocat",
      "message": "Add payment webhook handler",
      "timestamp": "2026-09-01T04:00:00Z",
      "risk_score": 45,
      "status": "blocked",
      "pr_number": 42
    }
  ],
  "edges": [
    { "source": "a1b2c3d", "target": "e4f5g6h" }
  ]
}
```

#### 4. Step-by-Step Implementation Backlog
1. Implement CORS whitelist and security headers middleware in `safelane/server/middleware.py`.
2. Build DAG traversal service in `safelane/services/graph_service.py` querying commit parents.
3. Develop SVG / Canvas commit graph visualization component in React.
4. Implement synthetic PR load benchmarking script `tests/benchmarks/load_test.py` utilizing Locust / `httpx`.

---

## 5. Complete Data Architecture

### 5.1 PostgreSQL Relational Schema (Complete SQL DDL)

```sql
-- SafeLane v2 Production PostgreSQL Schema
-- Migration 001_initial_schema.sql

-- 1. Users Table
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    github_id BIGINT NOT NULL UNIQUE,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_github_id ON users(github_id);

-- 2. GitHub Installations (OAuth / GitHub App Tenant Context)
-- Note: user_id is nullable with ON DELETE SET NULL so deleting a user does not wipe out organization repositories & history.
CREATE TABLE github_installations (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    installation_id BIGINT NOT NULL UNIQUE,
    account_login VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL DEFAULT 'Organization',
    app_id VARCHAR(64),
    cached_token_encrypted TEXT,
    token_expires_at TIMESTAMPTZ,
    permissions JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_installations_user ON github_installations(user_id);
CREATE INDEX idx_installations_gh_id ON github_installations(installation_id);

-- 3. Repositories Table
CREATE TABLE repositories (
    id BIGSERIAL PRIMARY KEY,
    installation_id BIGINT NOT NULL REFERENCES github_installations(id) ON DELETE CASCADE,
    github_repo_id BIGINT NOT NULL UNIQUE,
    owner VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    full_name VARCHAR(512) NOT NULL UNIQUE,
    default_branch VARCHAR(255) NOT NULL DEFAULT 'main',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    webhook_secret_encrypted TEXT,
    safety_score INT NOT NULL DEFAULT 100,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_repo_owner_name UNIQUE (owner, name)
);
CREATE INDEX idx_repos_installation ON repositories(installation_id);
CREATE INDEX idx_repos_full_name ON repositories(full_name);

-- 4. Pull Requests Table
CREATE TABLE pull_requests (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    pr_number INT NOT NULL,
    title VARCHAR(512) NOT NULL,
    body TEXT,
    state VARCHAR(50) NOT NULL DEFAULT 'open',
    head_sha VARCHAR(64) NOT NULL,
    base_branch VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    closed_at TIMESTAMPTZ,
    merged_at TIMESTAMPTZ,
    CONSTRAINT uq_repo_pr UNIQUE (repo_id, pr_number)
);
CREATE INDEX idx_prs_repo_number ON pull_requests(repo_id, pr_number);
CREATE INDEX idx_prs_state ON pull_requests(state);

-- 5. Analysis Records Table (Verdict Header)
CREATE TABLE analysis_records (
    id BIGSERIAL PRIMARY KEY,
    pr_id BIGINT NOT NULL REFERENCES pull_requests(id) ON DELETE CASCADE,
    commit_sha VARCHAR(64) NOT NULL,
    confidence_score INT NOT NULL CHECK (confidence_score BETWEEN 0 AND 100),
    decision VARCHAR(50) NOT NULL CHECK (decision IN ('greenlight', 'warning', 'blocked', 'insufficient_analysis')),
    risk_brief TEXT NOT NULL,
    rollback_playbook TEXT,
    execution_time_ms INT NOT NULL,
    token_usage_prompt INT NOT NULL DEFAULT 0,
    token_usage_completion INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_analysis_pr ON analysis_records(pr_id);
CREATE INDEX idx_analysis_decision ON analysis_records(decision);

-- 6. Evidence Results Table (4 Modules Output)
CREATE TABLE evidence_results (
    id BIGSERIAL PRIMARY KEY,
    analysis_id BIGINT NOT NULL REFERENCES analysis_records(id) ON DELETE CASCADE,
    module VARCHAR(64) NOT NULL CHECK (module IN ('change_intelligence', 'incident_memory', 'verification_readiness', 'release_context')),
    status VARCHAR(32) NOT NULL CHECK (status IN ('pass', 'warning', 'critical')),
    risk_score_modifier INT NOT NULL,
    findings JSONB NOT NULL DEFAULT '[]'::jsonb,
    recommended_action TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_evidence_analysis ON evidence_results(analysis_id);

-- 7. Security Preflight Findings Table
-- Note: file_path defaults to 'PR_METADATA' and allows NULL for PR title/body injection findings.
CREATE TABLE security_findings (
    id BIGSERIAL PRIMARY KEY,
    analysis_id BIGINT NOT NULL REFERENCES analysis_records(id) ON DELETE CASCADE,
    rule_id VARCHAR(128) NOT NULL,
    severity VARCHAR(32) NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
    file_path VARCHAR(1024) DEFAULT 'PR_METADATA',
    evidence TEXT NOT NULL,
    remediation TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_findings_analysis ON security_findings(analysis_id);
CREATE INDEX idx_findings_severity ON security_findings(severity);

-- 8. Activity / Sync Events Table
CREATE TABLE activity_events (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    event_type VARCHAR(64) NOT NULL,
    title VARCHAR(512) NOT NULL,
    description TEXT,
    severity VARCHAR(32) NOT NULL DEFAULT 'info',
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_activity_repo_time ON activity_events(repo_id, created_at DESC);

-- 9. Notifications Table
CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    repo_id BIGINT NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    pr_id BIGINT REFERENCES pull_requests(id) ON DELETE SET NULL,
    notification_type VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read, created_at DESC);
```

---

### 5.2 Qdrant Vector Collection Architecture

```text
Collection Name:    safelane_incidents
Vector Dimension:   1536 (OpenAI text-embedding-3-small) or 384 (FastEmbed BAAI/bge-small-en-v1.5)
Distance Metric:    Cosine
HNSW M:             16
HNSW ef_construct:  100

Payload Schema:
{
  "incident_id": "INC-2026-104",
  "repository": "acme/payment-gateway",
  "title": "Checkout DB Connection Pool Deadlock",
  "summary": "Improper async connection closure under load exhausted connection pool causing 504s.",
  "severity": "critical",
  "affected_files": [
    "src/database/pool.py",
    "src/api/checkout.py"
  ],
  "root_cause_tags": ["concurrency", "asyncpg", "connection_pool"],
  "resolved_at": "2026-05-10T14:20:00Z"
}

Qdrant Search Query DSL:
{
  "vector": [0.0142, -0.0521, 0.0891, ...],
  "filter": {
    "must": [
      { "key": "repository", "match": { "value": "acme/payment-gateway" } }
    ]
  },
  "limit": 3,
  "score_threshold": 0.72
}
```

---

## 6. Async Pipeline, Concurrency & Resilience Model

### 6.1 End-to-End Event Flow & Execution Timeline

```text
Timeline (ms)    Component                    Action
0ms              Webhook Receiver             HTTP POST /webhook/github received
2ms              HMAC Middleware              HMAC SHA-256 signature verified against DB secret
5ms              FastAPI Gateway              Dispatches async task, responds 202 Accepted to GitHub
10ms             GitHub Client                Fetches PR diff, changed file paths, and commit metadata
150ms            Input Sanitizer (inputs.py)  Applies NFKC normalization, null byte strip, 200k char cap
160ms            Security Preflight           Runs 5 regex families (Secrets, CI/CD, eval, SSL, Injections)
175ms            Orchestrator Agent           Dispatches 4 Evidence Modules concurrently via asyncio.wait_for()
                 ├─ Change Intelligence       Parses diff AST/regex + LLM summary (420ms)
                 ├─ Incident Memory           Embeds diff + queries Qdrant vector index (140ms)
                 ├─ Verification Readiness    Checks test file presence via GitHub API (210ms)
                 └─ Release Context           Evaluates holiday/weekend calendar rules (1ms)
600ms            Control & Evaluation         Validates output schema, checks file path grounding against changed_files (15ms)
620ms            Verdict Policy Engine        Computes weighted score, checks failure degradation & security penalties (2ms)
622ms            Optimistic Concurrency Chk   Verifies head_sha == current PR HEAD before writing (aborts if superseded) (3ms)
625ms            Database Persistence         Writes AnalysisRecord, EvidenceResult, SecurityFinding (25ms)
660ms            GitHub Publisher             Renders markdown table, posts comment + @copilot nudge (220ms)
890ms            Complete                     Analysis pipeline finished, metrics & spans exported
```

### 6.2 Bounded Execution & Reliability Matrix

| Component | Timeout | Max Retries | Fallback Behavior on Failure |
|---|---|---|---|
| **Webhook Ingestion** | 2.0s | 0 | 202 Accepted + Enqueue for retry |
| **GitHub API Client** | 10.0s | 3 (Exp Backoff) | Abort with typed `DiffFetchError` |
| **Security Preflight** | 1.5s | 0 | Yields `warning` finding with crash description |
| **Change Intelligence** | 15.0s | 1 | Regex fallback; if fatal/empty, halts to `INSUFFICIENT_ANALYSIS` |
| **Incident Memory (Qdrant)**| 5.0s | 2 | Degrades to status `warning` (modifier +10, correlation offline) |
| **Verification Readiness** | 10.0s | 2 | Returns `warning` (Manual verification needed, modifier +15) |
| **Release Context** | 1.0s | 0 | Fallback to local UTC server time evaluation |
| **Multi-Module Failure (≥2)**| N/A | 0 | Authoritative halt to `INSUFFICIENT_ANALYSIS` (`score=0`) |
| **Control & Evaluation** | 3.0s | 2 iterations | Escalates to `INSUFFICIENT_ANALYSIS` (`score=0`) |
| **GitHub Publisher** | 10.0s | 3 (Exp Backoff) | Logs error to DB, creates alert notification |

### 6.3 Canonical Verdict Decision State Machine

```text
                               CANONICAL VERDICT STATE MACHINE
                               
                               ┌────────────────────────┐
                               │  Evidence Collection   │
                               │  & Security Preflight  │
                               └───────────┬────────────┘
                                           │
                                           ▼
                                ┌──────────────────────┐
                    ┌───────────┤ Evaluation Gate      ├───────────┐
                    │           │ (Schema & Budgets)   │           │
                    │           └──────────┬───────────┘           │
                    │ Fail/Timeout         │ Pass                  │
                    │ or ≥2 Module Fails   │                       │
                    ▼                      ▼                       ▼
       ┌─────────────────────────┐  ┌──────────────┐  ┌─────────────────────────┐
       │  INSUFFICIENT_ANALYSIS  │  │ Base Score   │  │   SECURITY CRITICAL?    │
       │  (Analysis incomplete,  │  │ Calculation  │  │ (Secrets, Dangerous CI, │
       │   requires manual audit)│  └──────┬───────┘  │  Code Execution Eval)   │
       └─────────────────────────┘         │          └────────────┬────────────┘
                                           │                       │ YES
                                           ▼                       ▼
                               ┌───────────────────────┐ ┌───────────────────┐
                               │ Security Penalty &    │ │      BLOCK        │
                               │ Blocker Evaluation    ├─► (Score < 70, or   │
                               └───────────┬───────────┘ │  Critical finding,│
                                           │             │  Rollback Playbook│
                                           │             │  Generated)       │
                         ┌─────────────────┴────────────────┐└───────────────────┘
                         │ Score >= 85                      │ Score 70..84
                         │ 0 Warnings                       │ Non-critical warns
                         ▼                                  ▼
                ┌──────────────────┐               ┌──────────────────┐
                │    GREENLIGHT    │               │     WARNING      │
                │ (Safe to merge,  │               │ (Caution advisory│
                │  high confidence)│               │  review points)  │
                └──────────────────┘               └──────────────────┘
```

---

## 7. Observability, Telemetry & Evaluation Framework

### 7.1 OpenTelemetry Span Hierarchy & Semantic Conventions

```text
[HTTP POST /webhook/github] (trace_id: 4bf92f3577b34da6a3ce929d0e0e4736)
  │
  ├── [safelane.webhook.verify_hmac] ── duration: 1.2ms
  │
  └── [safelane.orchestrate] ── pr: #42, repo: acme/core
        │
        ├── [safelane.github.fetch_diff] ── duration: 180ms
        │
        ├── [safelane.preflight] ── duration: 8.4ms (rules_evaluated: 5, findings: 0)
        │
        ├── [safelane.evidence_gather] (concurrent)
        │     ├── [safelane.agent.change_intelligence] ── duration: 420ms
        │     ├── [safelane.agent.incident_memory] ── duration: 140ms
        │     ├── [safelane.agent.verification_readiness] ── duration: 210ms
        │     └── [safelane.agent.release_context] ── duration: 0.8ms
        │
        ├── [safelane.control_evaluator] ── duration: 15ms (validation: pass)
        │
        ├── [safelane.verdict_engine] ── score: 92, decision: GREENLIGHT
        │
        ├── [safelane.db.persist_verdict] ── duration: 22ms
        │
        └── [safelane.publisher.post_comment] ── duration: 240ms
```

### 7.2 Prometheus Metrics Specifications

```text
# Metric Definitions exported at /metrics:
safelane_analyses_total{decision="greenlight|warning|blocked|insufficient_analysis"} (Counter)
safelane_analysis_duration_seconds{quantile="0.5|0.9|0.99"} (Summary)
safelane_security_preflight_findings_total{severity="info|warning|critical", rule_id="..."} (Counter)
safelane_agent_execution_duration_seconds{agent_name="change|incident|vr|release"} (Histogram)
safelane_github_api_requests_total{endpoint="...", status="200|404|429|500"} (Counter)
safelane_qdrant_retrievals_total{hit="true|false"} (Counter)
safelane_db_connection_pool_active (Gauge)
```

### 7.3 Agent Evaluation & Bounded Feedback Loop

```text
┌────────────────┐     Output      ┌──────────────────────┐   Is Valid?    ┌─────────────────────┐
│  Agent LLM     ├────────────────►│ Control & Evaluator  ├───────────────►│ Pass to Verdict     │
│  Invocation    │                 │ (Schema & Grounding) │     (YES)      │ Policy Engine       │
└───────▲────────┘                 └──────────┬───────────┘                └─────────────────────┘
        │                                     │
        │ Targeted Feedback                   │ (NO, Retries < 2)
        └─────────────────────────────────────┘
                                              │ (NO, Retries >= 2)
                                              ▼
                                   ┌─────────────────────┐
                                   │ Terminal State:     │
                                   │ INSUFFICIENT        │
                                   │ ANALYSIS            │
                                   └─────────────────────┘
```

---

## 8. Implementation Strategy, Risk Analysis & Definition of Done

### 8.1 Phased Execution Order & Dependencies

```text
Phase 1 (Identity & Ingestion) ──────► Phase 2 (Sync & Engine) ──────► Phase 3 (Evaluation & Dash)
                                                                               │
Phase 5 (Persistence & Qdrant) ◄───── Phase 4 (Policy & Workspace) ◄───────────┘
        │
        ▼
Phase 6 (DX & Analytics) ────────────► Phase 7 (Hardening & Graph Visualizer)
```

### 8.2 Integration-First Verification Rules

Every feature must be traced end-to-end:
`GitHub Webhook Event → FastAPI Ingestion → Ingestion Validator → Orchestrator → 4 Evidence Modules → Evaluator → Canonical Verdict Engine → PostgreSQL / Qdrant → GitHub Publisher Comment → React Dashboard View`

A feature is considered complete ONLY when all 8 hops in the chain pass verification without mock placeholders or silent swallows.

### 8.3 Definition of Done Checklist

- [ ] Single unified FastAPI server entry point without duplicate services.
- [ ] Insecure PAT in JWT payload completely removed; OAuth 2.0 / GitHub App flow functional.
- [ ] Webhook HMAC SHA-256 verification operational on all incoming PR events.
- [ ] Duplicate verdict engine in `controller.py` deleted; canonical `verdict.py` authoritative.
- [ ] Pydantic invariant `<70` score = `blocked` decision strictly enforced without crashes.
- [ ] PostgreSQL 16 schema deployed with 9 tables and Alembic versioned migrations.
- [ ] Qdrant vector collection configured and integrated into Incident Memory agent.
- [ ] Dashboard, Workspace, Timeline, and Analytics backend APIs and UI views fully operational.
- [ ] SafeLane Developer CLI (`safelane check`) functional on local git repositories.
- [ ] OpenTelemetry distributed tracing and Prometheus `/metrics` operational.
- [ ] Permissive CORS removed; production security headers and rate limiting active.
- [ ] All unit, integration, and security tests passing.
- [ ] Stale "Prism" references, dead scaffolding (`foundry.py`, `function_app.py`, `mcp_servers/`), and unused dependencies purged.
