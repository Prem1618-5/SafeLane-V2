<div align="center">

# 🛡️ SafeLane v2
### *The Autonomous Change Assurance Fabric & Pre-Deployment Risk Gate for GitHub*

[![Tests](https://img.shields.io/badge/Tests-107%2F107%20Passed-10B981?style=for-the-badge&logo=pytest&logoColor=white)](file:///d:/Development%20Project/SafeLane%20v2/tests/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Unified%20Gateway-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Tailwind-61DAFB?style=for-the-badge&logo=react&logoColor=black)](file:///d:/Development%20Project/SafeLane%20v2/platform/frontend/)
[![OAuth](https://img.shields.io/badge/GitHub-OAuth%202.0%20PKCE-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

<br/>

> **"Tests pass" is not the same as "safe to ship."**  
> SafeLane v2 reads every GitHub pull request like a principal site reliability engineer — synthesizing deterministic security preflights, multi-agent evidence modules, calendar heuristics, and historical incident memory into a single mathematical **Deployment Confidence Score (0–100)** with actionable rollback playbooks and Copilot test nudges posted directly to the PR.

<br/>

```
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
       │  └───────────────────────────────────┼──────────────────────────────────────┘  │
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

</div>

---

## 📑 Table of Contents

1. [🌟 The "Why?": The Illusion of Green Checks](#-the-why-the-illusion-of-green-checks)
2. [💡 The "How": Solution Philosophy & First Principles](#-the-how-solution-philosophy--first-principles)
3. [🏛️ System Architecture](#️-system-architecture)
   - [3.1 End-to-End Orchestration Flow](#31-end-to-end-orchestration-flow)
   - [3.2 The Four Evidence Modules](#32-the-four-evidence-modules)
   - [3.3 Canonical Verdict & Mathematical Invariants](#33-canonical-verdict--mathematical-invariants)
   - [3.4 Security Preflight & Input Sanitization](#34-security-preflight--input-sanitization)
4. [💻 Codebase Tour & Directory Structure](#-codebase-tour--directory-structure)
5. [⚡ Interactive Walkthrough & Getting Started](#-interactive-walkthrough--getting-started)
   - [5.1 Prerequisites & 1-Minute Setup](#51-prerequisites--1-minute-setup)
   - [5.2 GitHub OAuth App Configuration](#52-github-oauth-app-configuration)
   - [5.3 Running the Unified Server & Dashboard](#53-running-the-unified-server--dashboard)
   - [5.4 Simulating Webhooks & Test Suite Execution](#54-simulating-webhooks--test-suite-execution)
6. [📊 UI/UX Experience: Modern React Dashboard](#-uiux-experience-modern-react-dashboard)
7. [🧪 Verification & Invariant Testing Matrix](#-verification--invariant-testing-matrix)
8. [🧠 Applied Skills & Design Intelligence (Compact Note)](#-applied-skills--design-intelligence-compact-note)

---

## 🌟 The "Why?": The Illusion of Green Checks

Continuous Integration (CI) answers one simple question: **"Did the code compile and did the existing tests pass?"**

It never asks the questions that prevent real production outages:
- 💥 **Did a refactor delete a `try...catch` block or `@retry` decorator?** CI passes because the happy path works, but the first transient network blip will cascade into an outage.
- 💣 **Did an unindexed schema migration execute `DROP COLUMN` or `TRUNCATE`?** The syntax is valid, so CI passes, but production locks up immediately upon deployment.
- 🕒 **Is someone shipping a critical payment gateway change at 5:45 PM on a Friday before a long holiday weekend?** CI has no concept of calendar risk or human fatigue.
- 🔄 **Has this exact modified file caused 3 high-severity production incidents in the last 90 days?** CI has no memory of past postmortems.
- ⚠️ **Did a 400-line PR add complex business logic while deleting test files?** CI passes because the remaining tests succeed, leaving new branches completely untested.
- 🔓 **Did a developer accidentally commit a private key, an unpinned GitHub Action, or an `eval()` statement?**

```text
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ Typical CI Pipeline:                                                                      │
│ [Code Committed] ──► [Linter Passed] ──► [Unit Tests Passed] ──► [Merged] ──► 💥 Outage!   │
│                                                                                           │
│ SafeLane v2 Change Assurance Fabric:                                                      │
│ [Code Committed] ──► [Deterministic Security Preflight]                                   │
│                           ├── Secrets & CI/CD Scanner                                     │
│                           ├── Change Intel (AST & Deleted Safety Mechanisms)              │
│                           ├── Incident Memory (Historical Outage Matching)                │
│                           ├── Verification Readiness (Test Suite & Copilot Nudge)         │
│                           └── Release Context (Calendar & Deployment Timing)              │
│                      ──► [Canonical Verdict: Score 0-100] ──► 🛡️ Safe Release Assured    │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

SafeLane fills this critical operational gap. It acts as an automated, objective change reviewer that protects engineering teams from high-risk, silent regressions.

---

## 💡 The "How": Solution Philosophy & First Principles

SafeLane was built upon five strict architectural pillars:

### 1. Deterministic Security Preflight Overrides AI
AI models are creative, but safety must be mathematically predictable. SafeLane runs a zero-cost, deterministic regex and AST scanner **before** any AI or evidence module dispatches. If a hardcoded secret, `eval()`, or unpinned action is detected, the penalty is applied instantly and deterministically. AI cannot "hallucinate" away a security failure.

### 2. Multi-Angle Parallel Evidence Synthesis
Instead of sending a monolithic 20,000-token prompt to an LLM and hoping for a thorough review, SafeLane isolates risk into **four distinct dimensions** evaluated concurrently via `asyncio.gather()`:
- **Structural Code Risk** (`Change Intelligence`)
- **Historical Postmortem Memory** (`Incident Memory`)
- **Test Coverage Adequacy** (`Verification Readiness`)
- **Temporal & Calendar Hazard** (`Release Context`)

### 3. Strict Mathematical Scoring & Invariant Enforcement
Scores are calculated via weighted arithmetic:
$$\text{Base Score} = 100 - \sum_{i=1}^{4} (\text{Modifier}_i \times \text{Weight}_i)$$

Where weights are strictly bound:
- **Change Intelligence:** $30\%$
- **Incident Memory:** $25\%$
- **Verification Readiness:** $25\%$
- **Release Context:** $20\%$

Security penalties (Warning: $-8\text{ pts}$, Critical: $-25\text{ pts}$, capped at $-40\text{ pts}$) deduct from the base score.
- **Score $\ge 70$ and 0 Critical Findings $\implies$ `GREENLIGHT`**
- **Score $< 70$ OR $\ge 1$ Critical Finding $\implies$ `BLOCKED`**
- Invariant: A `GREENLIGHT` verdict **never** generates a rollback playbook; a `BLOCKED` verdict **always** generates an automated `git revert` playbook.

### 4. Zero Secret Exposure & Frictionless 1-Click Identity
No manual GitHub Personal Access Tokens (PATs) in the browser. SafeLane features a 1-click GitHub OAuth 2.0 PKCE flow. OAuth tokens are encrypted at rest using **Fernet AES-256-CBC** symmetric encryption in the backend database. Client-side session JWTs contain **only** `github_username`, `github_id`, and `exp` — zero raw tokens ever touch the browser.

### 5. Actionable Remediation (Never Just Complain)
When SafeLane blocks a PR, it doesn't leave the developer stranded:
- It outputs a step-by-step **Git Rollback Playbook** targeting the exact commit SHA (`git checkout main`, `git revert <SHA>`, etc.).
- When missing test files are detected, it posts an actionable `@copilot Please generate unit tests for...` nudge directly on GitHub.

---

## 🏛️ System Architecture

SafeLane v2 runs as a unified, modular platform where the analysis engine, webhook ingestion gateway, OAuth service, and React dashboard live under a single production service.

```mermaid
flowchart TD
    subgraph Ingestion ["1. Identity & Event Ingestion"]
        GH_EVT[GitHub Webhook / PR Event] -->|HMAC-SHA256 Signed| Webhook["/webhook/pr (FastAPI)"]
        UI_CLI[Developer / Web UI] -->|GitHub OAuth 2.0 / JWT| AppAuth["/api/auth (OAuth Router)"]
    end

    subgraph PlatformDB ["2. Encrypted State & Persistence"]
        AppAuth --> DB[("PostgreSQL 16 / SQLite (Async SQLAlchemy)")]
        DB --- Crypto["Fernet AES-256 Symmetric Encryption"]
    end

    subgraph Fabric ["3. SafeLane Fabric Orchestration Engine"]
        Webhook -->|Normalize & Bounds Check| Inputs["safelane/fabric/inputs.py (NFKC, 200k diff cap)"]
        Inputs -->|PRPayload| Controller["safelane/fabric/controller.py"]
        
        Controller -->|1. Deterministic Pass| Preflight["safelane/fabric/security_preflight.py\n(Secrets, CI/CD, eval, Injection)"]
        
        subgraph ParallelModules ["2. Concurrent Evidence Dispatch (asyncio.gather, 30s timeout)"]
            CI["Change Intelligence\n(AST, removed try/catch, SQL drops)"]
            IM["Incident Memory\n(Postmortem Correlation & Search)"]
            VR["Verification Readiness\n(Test suite file inspection)"]
            RC["Release Context\n(Calendar, Friday, US Holidays)"]
        end
        
        Controller --> ParallelModules
        Preflight --> Verdict["safelane/fabric/verdict.py\n(Canonical Scoring Math & Invariants)"]
        ParallelModules --> Verdict
    end

    subgraph Publishing ["4. Output & Actionable Gate"]
        Verdict -->|VerdictReport| Publisher["safelane/fabric/publisher.py"]
        Publisher -->|Fixed Markdown Comment| GH_PR[GitHub Pull Request]
        Publisher -->|@copilot Nudge| Copilot[Copilot Test Bot]
        Verdict -->|Persist AnalysisRecord| DB
        DB --> DashboardUI["React 18 + Vite + Tailwind Dashboard"]
    end
```

---

### 3.1 End-to-End Orchestration Flow

1. **Webhook Reception**: GitHub fires a PR event (`opened`, `synchronize`, `reopened`) to `/webhook/pr`. SafeLane verifies the signature using constant-time `hmac.compare_digest`.
2. **Context Resolution**: The repository's encrypted OAuth token is resolved from the database via `get_repo_context()` and decrypted on-the-fly.
3. **Payload Sanitization**: Untrusted diffs and file paths pass through `safelane/fabric/inputs.py`, which strips null bytes (`\x00`), normalizes unicode to NFKC, and bounds diffs to 200,000 characters.
4. **Security Preflight**: Static regex scanner detects credentials, unpinned actions, and command injections.
5. **Parallel Analysis**: Four evidence modules execute concurrently with 30-second timeouts and safe fallback handlers.
6. **Verdict Formulation**: Canonical `verdict.py` computes the weighted score, applies security penalties, verifies invariants, and generates rollback scripts.
7. **Actionable Publishing**: Fixed-template markdown comment is posted to GitHub with 3-attempt exponential backoff retry logic.

---

### 3.2 The Four Evidence Modules

| Module | Inspection Target | Risk Rules & Heuristics | Modifier Output |
| :--- | :--- | :--- | :--- |
| **🔍 Change Intelligence**<br/>`safelane/evidence/change_intelligence.py` | Diff structure, AST patterns, removed lines | • Removed `try/except/catch` blocks ($+30$ risk)<br/>• Removed `@retry`/backoff decorators ($+30$ risk)<br/>• Dangerous SQL (`DROP TABLE`, `ALTER COLUMN`) ($+60$ risk)<br/>• Diff $>500$ lines ($+30$ risk) / empty diff ($+20$ risk)<br/>• Optional Azure OpenAI semantic enrichment | `0–100` modifier<br/>*(Pass / Warning / Critical)* |
| **🧠 Incident Memory**<br/>`safelane/evidence/incident_memory.py` | Changed files vs historical incident store | • Matches modified files/stems against historical postmortems<br/>• $\ge 3$ past incidents or any critical incident ($+60$ risk)<br/>• $1–2$ past incidents ($+30$ risk)<br/>• Safe fallback to mock/clean if no history is configured | `0–100` modifier<br/>*(Pass / Warning / Critical)* |
| **🧪 Verification Readiness**<br/>`safelane/evidence/verification_readiness.py` | Unit test file presence on GitHub | • Detects deleted test files (`test_*.py`) ($+60$ risk)<br/>• Queries GitHub Contents API for matching `tests/test_<name>.py`<br/>• Missing tests trigger automated `@copilot` prompt generator | `0–100` modifier<br/>*(Pass / Warning / Critical)* |
| **📅 Release Context**<br/>`safelane/evidence/release_context.py` | PR submission timestamp (UTC) | • Friday deployment ($+15$ risk)<br/>• Weekend deployment ($+25$ risk)<br/>• Off-hours 20:00–06:00 UTC ($+15$ risk)<br/>• US Federal Holidays & holiday eve ($+10–20$ risk) | `0–100` modifier<br/>*(Pass / Warning / Critical)* |

---

### 3.3 Canonical Verdict & Mathematical Invariants

The verdict pipeline is strictly governed by Pydantic v2 invariants defined in `safelane/contracts.py`:

```python
# Invariant: Score < 70 forces BLOCKED decision
if confidence_score < 70:
    decision = "blocked"

# Invariant: Any Critical finding forces BLOCKED decision
if any(finding.severity == "critical" for finding in security_findings) or \
   any(result.status == "critical" for result in evidence_results):
    decision = "blocked"

# Invariant: GREENLIGHT never has a rollback playbook; BLOCKED always does
if decision == "greenlight":
    rollback_playbook = None
elif decision == "blocked" and head_sha:
    rollback_playbook = f"git checkout main\ngit revert {head_sha} -m 1\ngit push origin main"
```

---

### 3.4 Security Preflight & Input Sanitization

Static detection families executed before any agent reasoning:

```text
┌──────────────────────────┬──────────────────────────────────────────────────────────┬──────────┐
│ Rule Family              │ Patterns Detected                                        │ Severity │
├──────────────────────────┼──────────────────────────────────────────────────────────┼──────────┤
│ Secret Exposure          │ GitHub (ghp_), OpenAI (sk-), AWS (AKIA), PEM Private Keys│ CRITICAL │
│ CI/CD Hardening          │ `permissions: write-all`, `pull_request_target` checkout │ CRITICAL │
│ Dangerous Execution      │ `eval()`, `exec()`, `subprocess(shell=True)`, `pickle`   │ WARNING  │
│ Insecure Transport       │ `verify=False`, `ssl.CERT_NONE`, `--no-check-certificate`│ WARNING  │
│ Prompt Injection Markers │ `ignore previous instructions`, `you are now`, `system:` │ WARNING  │
└──────────────────────────┴──────────────────────────────────────────────────────────┴──────────┘
```

---

## 💻 Codebase Tour & Directory Structure

```
d:\Development Project\SafeLane v2\
├── conftest.py                             # Root test harness & sys.path configuration
├── pyproject.toml                          # Python 3.12+ project config & pytest settings
├── requirements.txt                        # Clean, minimal production dependencies
├── docker-compose.yml                      # Single-service unified deployment
├── Dockerfile.safelane                     # Production container spec
│
├── safelane/                               # Core Change Assurance Engine
│   ├── contracts.py                        # Pydantic v2 data models, weights & invariants
│   ├── adapters/
│   │   └── github.py                       # Unified GitHub Webhook router & DB context resolver
│   ├── evidence/                           # The 4 Multi-Angle Evidence Modules
│   │   ├── change_intelligence.py          # AST diff analysis, removed safety checks, SQL drops
│   │   ├── incident_memory.py              # Historical postmortem correlation engine
│   │   ├── incident_store.py               # Incident schema & structured memory lookup
│   │   ├── release_context.py              # Temporal calendar & US holiday heuristics
│   │   └── verification_readiness.py       # Test coverage inspection & Copilot nudge
│   └── fabric/                             # Orchestration & Evaluation
│       ├── controller.py                   # Async concurrent orchestrator (asyncio.gather)
│       ├── inputs.py                       # Input sanitization (NFKC normalization, bounds)
│       ├── security_preflight.py           # Deterministic regex scanner for secrets/code exec
│       ├── verdict.py                      # Authoritative score calculator & rollback builder
│       └── publisher.py                    # Fixed-template PR markdown comment publisher
│
├── platform/                               # Platform Gateway & Frontend
│   ├── server/                             # FastAPI Backend Service
│   │   ├── app.py                          # Unified FastAPI application entry point & SPA host
│   │   ├── routers/
│   │   │   ├── auth.py                     # GitHub OAuth 2.0 login & callback handlers
│   │   │   ├── github_setup.py             # User repository synchronization endpoints
│   │   │   ├── registrations.py            # Repository connection CRUD & enable/disable
│   │   │   └── dashboard.py                # Metrics, safety scores, and PR analysis APIs
│   │   └── services/
│   │       ├── auth_service.py             # Fernet symmetric encryption & JWT session tokens
│   │       ├── db.py                       # Async SQLAlchemy ORM (Postgres/SQLite)
│   │       ├── github_service.py           # GitHub OAuth token exchange & user APIs
│   │       └── sync_service.py             # Background PR & activity synchronization
│   └── frontend/                           # Modern React 18 + Tailwind Dashboard
│       ├── package.json                    # Frontend dependencies (React, Vite, Lucide, Tailwind)
│       ├── vite.config.js                  # Vite configuration & proxy routes
│       ├── tailwind.config.js              # Tailwind CSS design system configuration
│       ├── src/
│       │   ├── main.jsx / App.jsx          # Root application layout & routing
│       │   ├── api.js / auth.jsx           # JWT fetch client & AuthProvider context
│       │   ├── pages/                      # SignIn, Repos, RepoDashboard, PRDetail, Callback
│       │   └── components/                 # ScoreGauge, SafetyBadge, EvidenceCard, Playbook
│       └── dist/                           # Production-compiled assets served by FastAPI
│
└── tests/                                  # Comprehensive Test Suite (107 Tests)
    ├── integration/
    │   └── test_v2_fabric.py               # End-to-end multi-agent orchestration tests
    └── unit/
        ├── test_oauth.py                   # OAuth code exchange & JWT security tests
        ├── test_verdict_unified.py         # Verdict invariant & AST single-authority tests
        ├── test_webhook_hmac.py            # Webhook HMAC verification & event routing tests
        ├── test_dashboard_api.py           # Dashboard API auth guards & detail tests
        ├── test_db_credentials.py          # DB token lookup & env fallback tests
        ├── test_security_preflight.py      # Secret detection & preflight regex tests
        ├── test_change_intelligence.py     # Diff analysis & AST inspection tests
        ├── test_incident_memory.py         # Incident memory correlation tests
        ├── test_verification_readiness.py  # Test file existence & deletion tests
        ├── test_release_context.py         # Holiday & weekend timing tests
        ├── test_inputs.py                  # Unicode normalization & length bounds tests
        ├── test_publisher.py               # PR markdown formatting tests
        └── test_server.py                  # Server health & webhook tests
```

---

## ⚡ Interactive Walkthrough & Getting Started

### 5.1 Prerequisites & 1-Minute Setup

SafeLane v2 requires **Python 3.12+** and **Node.js 18+**.

```bash
# 1. Clone repository
git clone https://github.com/Vishal-047/safe-lane_demo.git
cd "SafeLane v2"

# 2. Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Copy environment template
cp .env.example .env
```

---

### 5.2 GitHub OAuth App Configuration

To enable 1-Click sign-in without manual PATs:
1. Navigate to **[GitHub Developer Settings → OAuth Apps → New OAuth App](https://github.com/settings/applications/new)**.
2. Fill in:
   - **Application Name**: `SafeLane Change Assurance`
   - **Homepage URL**: `http://localhost:8000`
   - **Authorization Callback URL**: `http://localhost:8000/api/auth/github/callback`
3. Generate a Client Secret and add them to your `.env`:

```env
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here
JWT_SECRET=generate_with_secrets_token_hex_32
ENCRYPTION_KEY=generate_with_fernet_generate_key
GITHUB_WEBHOOK_SECRET=your_webhook_hmac_secret
```

*(You can generate `ENCRYPTION_KEY` quickly using `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`)*

---

### 5.3 Running the Unified Server & Dashboard

Start the single unified FastAPI service (which serves both the API and the compiled React SPA):

```bash
# Start backend server on port 8000
uvicorn platform.server.app:app --reload --port 8000
```

- 🌐 **Web Dashboard & Onboarding**: Open [`http://localhost:8000`](http://localhost:8000) in your browser.
- 🩺 **Health Check**: [`http://localhost:8000/health`](http://localhost:8000/health)
- 📖 **Interactive API Documentation**: [`http://localhost:8000/docs`](http://localhost:8000/docs)

*(For frontend active development with Hot Module Replacement, run `cd platform/frontend && npm run dev` on port 5173).*

---

### 5.4 Simulating Webhooks & Test Suite Execution

Run the complete 107-test suite to verify the entire system:

```bash
# Run all 107 tests
python -m pytest tests/ -v

# Run only new unified architecture tests
python -m pytest tests/unit/test_oauth.py tests/unit/test_verdict_unified.py tests/unit/test_webhook_hmac.py tests/unit/test_dashboard_api.py tests/unit/test_db_credentials.py -v
```

**Simulate a Pull Request Webhook via cURL:**

```bash
curl -X POST "http://localhost:8000/api/safelane/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "pr_number": 101,
       "repo": "acme/payment-service",
       "changed_files": ["services/payment.py", "migrations/003_drop_table.sql"],
       "diff": "- try:\n-     charge_card()\n- except NetworkError:\n-     retry()\n+ DROP TABLE card_tokens;",
       "timestamp": "2026-09-04T17:30:00Z",
       "head_sha": "a1b2c3d4e5f6"
     }'
```

---

## 📊 UI/UX Experience: Modern React Dashboard

SafeLane v2 features a clean, responsive single-page application built with React 18, Tailwind CSS, and Lucide icons:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 🛡️ SafeLane      📊 Repositories    🔔 Activity    ⚙️ Settings          👤 vishal-047 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  acme / payment-service                         Deployment Safety Score               │
│  Main Branch • Last Synced 2m ago                     ┌─────────┐                      │
│                                                       │   42%   │  🔴 BLOCKED          │
│                                                       └─────────┘                      │
│                                                                                        │
│  Evidence Breakdown                                                                    │
│  ┌─────────────────────────────────┐   ┌─────────────────────────────────┐             │
│  │ 🔍 Change Intelligence: CRITICAL│   │ 🧠 Incident Memory: WARNING     │             │
│  │ • Removed try/catch error block │   │ • Modified payment.py triggered │             │
│  │ • Unsafe SQL: DROP TABLE tokens │   │   INC-042 outage in May 2026    │             │
│  └─────────────────────────────────┘   └─────────────────────────────────┘             │
│  ┌─────────────────────────────────┐   ┌─────────────────────────────────┐             │
│  │ 🧪 Verification Readiness: PASS │   │ 📅 Release Context: WARNING     │             │
│  │ • Test suite test_payment.py ok │   │ • Friday 5:30 PM deployment     │             │
│  │ • No test files deleted         │   │ • Approaching Labor Day weekend │             │
│  └─────────────────────────────────┘   └─────────────────────────────────┘             │
│                                                                                        │
│  📋 Automated Rollback Playbook                                                        │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐ │
│  │ $ git checkout main                                                               │ │
│  │ $ git revert a1b2c3d4e5f6 -m 1                                                    │ │
│  │ $ git push origin main                                                            │ │
│  └───────────────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧪 Verification & Invariant Testing Matrix

SafeLane maintains a comprehensive automated test suite with **107 passing tests**:

| Test Suite | Total Tests | Focus & Invariants Covered |
| :--- | :---: | :--- |
| [`test_oauth.py`](file:///d:/Development%20Project/SafeLane%20v2/tests/unit/test_oauth.py) | **9** | • Token encryption/decryption roundtrip<br/>• JWT payload contains **zero** raw tokens<br/>• Tampered JWT rejection<br/>• OAuth code exchange mocking |
| [`test_verdict_unified.py`](file:///d:/Development%20Project/SafeLane%20v2/tests/unit/test_verdict_unified.py) | **9** | • AST verification that only 1 `build_verdict` exists<br/>• Score 60–69 bug fix verification<br/>• Critical finding $\implies$ `BLOCKED` invariant<br/>• Rollback playbook inclusion logic |
| [`test_webhook_hmac.py`](file:///d:/Development%20Project/SafeLane%20v2/tests/unit/test_webhook_hmac.py) | **10** | • Valid HMAC-SHA256 signature verification<br/>• Invalid/tampered signature rejection (401)<br/>• `hmac.compare_digest` constant-time verification<br/>• Non-PR event filtering (`opened`, `synchronize`, `reopened`) |
| [`test_dashboard_api.py`](file:///d:/Development%20Project/SafeLane%20v2/tests/unit/test_dashboard_api.py) | **8** | • Unauthenticated 401 guards<br/>• Repository authorization & ownership checks<br/>• PR detail & evidence result JSON parsing<br/>• `/api/auth/me` endpoint sanitization |
| [`test_db_credentials.py`](file:///d:/Development%20Project/SafeLane%20v2/tests/unit/test_db_credentials.py) | **6** | • Dynamic DB token resolution by repo name<br/>• Inactive registration filtering<br/>• Local dev `GITHUB_TOKEN` env fallback |
| **Core Evidence & Preflight** | **65** | • Change intelligence AST checks (10 tests)<br/>• Incident memory postmortem lookup (7 tests)<br/>• Verification readiness & deleted test detection (7 tests)<br/>• Release context holiday/timing calculations (7 tests)<br/>• Security preflight regex & secret redaction (11 tests)<br/>• Input sanitization & bounds capping (6 tests)<br/>• Publisher markdown formatting & `@copilot` nudges (4 tests)<br/>• End-to-end fabric integration (3 tests)<br/>• Server webhook compatibility (5 tests)<br/>• Verdict weights & boundary calculations (8 tests) |
| **Total Test Count** | **107** | **100% Passing (0 Failures, 0 Regressions)** |

---

## 🧠 Applied Skills & Design Intelligence (Compact Note)

> [!NOTE]
> **Engineering & Design Craftsmanship:**
> 
> SafeLane v2 was built applying modern design and architectural intelligence:
> - **Premium UI & Design Engineering** (`premium-frontend-ui`, `ui-ux-pro-max`): Implemented a clean, high-contrast, accessible visual design system with clear visual hierarchy, SVG score gauges, responsive layouts, and zero visual clutter.
> - **Modern Web Guidance** (`modern-web-guidance`): Applied secure OAuth 2.0 PKCE principles, client-side routing fallback handlers, strict CORS policies, and token-free JWT sessions.
> - **Agent Architecture & Evaluation Foundations**: Multi-agent parallelization with bounded timeouts (`asyncio.gather`), deterministic static preflight overrides, and graceful degradation principles.

---

<div align="center">

**SafeLane v2** — *Engineered with precision for safer software delivery.*  
Made with ❤️ for GitHub developers and engineering reliability teams.

</div>
