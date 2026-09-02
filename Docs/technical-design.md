# Technical Design & Architecture: SafeLane v2

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
        Webhook -->|Normalize & Bounds Check| Inputs["safelane/fabric/inputs.py (NFKC, 100k diff cap)"]
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

### End-to-End Orchestration Flow

1. **Webhook Reception**: GitHub fires a PR event (`opened`, `synchronize`, `reopened`) to `/webhook/pr`. SafeLane verifies the signature using constant-time `hmac.compare_digest`.
2. **Context Resolution**: The repository's encrypted OAuth token is resolved from the database via `get_repo_context()` and decrypted on-the-fly.
3. **Payload Sanitization**: Untrusted diffs and file paths pass through `safelane/fabric/inputs.py`, which strips null bytes (`\x00`), normalizes unicode to NFKC, and bounds diffs to 100,000 characters. The 100k cap is a request/token budget boundary — diffs beyond it are truncated for LLM input, not penalized for size.
4. **Security Preflight**: Static regex scanner detects credentials, unpinned actions, and command injections.
5. **Parallel Analysis**: Four evidence modules execute concurrently with 30-second timeouts and safe fallback handlers.
6. **Verdict Formulation**: Canonical `verdict.py` computes the weighted score, applies security penalties, verifies invariants, and generates rollback scripts.
7. **Actionable Publishing**: Fixed-template markdown comment is posted to GitHub with 3-attempt exponential backoff retry logic.

### The Four Evidence Modules

| Module | Inspection Target | Risk Rules & Heuristics | Modifier Output |
| :--- | :--- | :--- | :--- |
| **🔍 Change Intelligence**<br/>`safelane/evidence/change_intelligence.py` | Diff structure, AST patterns, removed lines | • Removed `try/except/catch` blocks (+30 risk)<br/>• Removed `@retry`/backoff decorators (+30 risk)<br/>• Dangerous SQL (`DROP TABLE`, `ALTER COLUMN`) (+60 risk)<br/>• Diff >500 lines (+30 risk) / empty diff (+20 risk)<br/>• Optional Azure OpenAI semantic enrichment | `0–100` modifier<br/>*(Pass / Warning / Critical)* |
| **🧠 Incident Memory**<br/>`safelane/evidence/incident_memory.py` | Changed files vs historical incident store | • Matches modified files/stems against historical postmortems<br/>• >= 3 past incidents or any critical incident (+60 risk)<br/>• 1–2 past incidents (+30 risk)<br/>• Safe fallback to mock/clean if no history is configured | `0–100` modifier<br/>*(Pass / Warning / Critical)* |
| **🧪 Verification Readiness**<br/>`safelane/evidence/verification_readiness.py` | Unit test file presence on GitHub | • Detects deleted test files (`test_*.py`) (+60 risk)<br/>• Queries GitHub Contents API for matching `tests/test_<name>.py`<br/>• Missing tests trigger automated `@copilot` prompt generator | `0–100` modifier<br/>*(Pass / Warning / Critical)* |
| **📅 Release Context**<br/>`safelane/evidence/release_context.py` | PR submission timestamp (UTC) | • Friday deployment (+15 risk)<br/>• Weekend deployment (+25 risk)<br/>• Off-hours 20:00–06:00 UTC (+15 risk)<br/>• US Federal Holidays & holiday eve (+10–20 risk) | `0–100` modifier<br/>*(Pass / Warning / Critical)* |

### Canonical Verdict & Mathematical Invariants

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
    # Generates a safe branch-based revert sequence
    pass
```

### Security Preflight & Input Sanitization

Static detection families executed before any agent reasoning:

| Rule Family | Patterns Detected | Severity |
| :--- | :--- | :--- |
| Secret Exposure | GitHub (ghp_), OpenAI (sk-), AWS (AKIA), PEM Private Keys | CRITICAL |
| CI/CD Hardening | `permissions: write-all`, `pull_request_target` checkout | CRITICAL |
| Dangerous Execution | `eval()`, `exec()`, `subprocess(shell=True)`, `pickle` | WARNING |
| Insecure Transport | `verify=False`, `ssl.CERT_NONE`, `--no-check-certificate` | WARNING |
| Prompt Injection | `ignore previous instructions`, `you are now`, `system:` | WARNING |

## 💻 Codebase Tour & Directory Structure

```text
d:\Development Project\SafeLane v2\
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
│   │   ├── routers/                        # API routes (Auth, Dashboard, Registrations, Sync)
│   │   └── services/                       # DB, GitHub, Auth & Background Sync services
│   └── frontend/                           # Modern React 18 + Tailwind Dashboard
│       └── src/
│           ├── components/                 # ScoreGauge, SecurityAlert, EvidenceCard
│           └── pages/                      # Repositories, PRDetail, SignIn
│
└── tests/                                  # Comprehensive Test Suite (107+ Tests)
    ├── integration/                        # End-to-end multi-agent orchestration tests
    └── unit/                               # Core business logic tests
```

## 🧪 Verification & Invariant Testing Matrix

SafeLane maintains a comprehensive automated test suite with **107+ passing tests**:

| Test Suite | Total Tests | Focus & Invariants Covered |
| :--- | :---: | :--- |
| `test_oauth.py` | **9** | • Token encryption/decryption roundtrip<br/>• JWT payload contains **zero** raw tokens<br/>• Tampered JWT rejection<br/>• OAuth code exchange mocking |
| `test_verdict_unified.py` | **9** | • AST verification that only 1 `build_verdict` exists<br/>• Critical finding => `BLOCKED` invariant<br/>• Rollback playbook inclusion logic |
| `test_webhook_hmac.py` | **10** | • Valid HMAC-SHA256 signature verification<br/>• Invalid/tampered signature rejection (401)<br/>• Non-PR event filtering |
| `test_dashboard_api.py` | **8** | • Unauthenticated 401 guards<br/>• Repository authorization & ownership checks |
| `test_db_credentials.py` | **6** | • Dynamic DB token resolution by repo name<br/>• Local dev `GITHUB_TOKEN` env fallback |
| **Core Evidence & Preflight** | **65** | • AST, Memory, Verification, Release context, Security Preflight testing |
| **Total Test Count** | **107+** | **100% Passing (0 Failures, 0 Regressions)** |
