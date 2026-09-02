# SafeLane — Instructions & Tasks

## 1. Confirmed Problems

### Critical
1. Setup Platform stores repository registrations/credentials, but the orchestrator does not consume them; it relies on mock registration/global `GITHUB_TOKEN`.
2. Webhook secret verification expects HMAC, but the generated workflow does not provide the signature.

### High
3. README references non-existent `agents.orchestrator.server`.
4. GitHub fetch failures can lead to incomplete/empty analysis.
5. Azure incident-ingestion functions are stubbed.
6. Incident uploader/reader schemas do not match.
7. Foundry helpers are not on the live orchestration path.
8. PAT/credential handling exposes sensitive material to browser-side JWT consumers.
9. Verdict logic is duplicated and inconsistent.
10. Tests emphasize alternate/dead paths more than the live path.

### Medium / Structural
11. `openai` dependency was missing in the audit runtime.
12. Dependency set is broader than required.
13. CORS is too permissive.
14. No production migration/versioning mechanism.
15. User/registration relationships and uniqueness constraints need correction.
16. Azure Search configuration is not correctly passed into live incident analysis.
17. `SAFELANE_FREE_TIER_LIMIT` appears dead.
18. Foundry/tracing helpers are disconnected.
19. MCP directory is scaffolding, not a live server.
20. Azure Function ingestion is scaffolding.
21. Old `Prism` references remain.
22. Duplicate verdict implementations remain.

### Preserve
- typed contracts
- four existing evidence modules
- deterministic Security Preflight
- constrained GitHub publisher
- existing test foundation

## 2. Final Architecture

```text
GitHub
  │ PR / Webhook
  ▼
FastAPI Ingestion
  │
  ▼
Orchestrator Agent
  ├── Change Intelligence Agent
  ├── Incident Memory Agent
  ├── Verification Readiness Agent
  └── Release Context Agent
  │
  ▼
Control & Evaluation
  ├── schema validation
  ├── evidence validation
  ├── quality checks
  ├── time/token budgets
  └── bounded retry + feedback
  │
  ▼
Deterministic Safety & Policy
  ├── Security Preflight
  └── Verdict / Policy Engine
  │
  ├── PostgreSQL
  ├── Qdrant
  └── GitHub Publisher
```

Infrastructure:
- Azure AI Foundry — agent/model runtime
- PostgreSQL — durable application state
- Qdrant — incident-memory/vector retrieval
- GitHub — repositories, PRs, webhooks, comments

## 3. Component Responsibilities

### GitHub
OAuth/GitHub App authorization, repository permissions, PR/diff/commit/review/workflow data, webhooks, comments. Do not expose credentials to users or rely on manual PAT entry.

### FastAPI
API boundary, webhook verification, sync triggers, dashboard APIs, analysis initiation, health/status. No complex reasoning.

### Orchestrator Agent
Build analysis context, invoke four agents, coordinate parallelism, collect results, manage evaluator feedback, retries, workflow state. Never run without budgets or override deterministic policy.

### Change Intelligence Agent
Analyze changed files/regions, risk, impact, evidence, severity, confidence.

### Incident Memory Agent
Retrieve similar historical incidents from Qdrant, rank relevance, explain why they matter, and safely return no-result when history is unavailable.

### Verification Readiness Agent
Inspect tests and verification evidence, identify gaps, assess whether the change is reasonably verifiable. Never equate tests with guaranteed correctness.

### Release Context Agent
Assess deployment/release context and operational risk. Never invent missing context.

### Control & Evaluation
Validate schema, evidence, quality, consistency; enforce token/time/iteration budgets; decide retry/failure state.

### Security Preflight
Deterministic checks for secrets, risky CI/CD, dangerous execution, auth/TLS weakness, prompt-injection indicators, and other hard policies.

### Verdict / Policy Engine
Single canonical deterministic authority. Suggested states: `GREENLIGHT`, `WARNING`, `BLOCK`, `INSUFFICIENT_ANALYSIS`.

### PostgreSQL
Users, GitHub installations, repository connections/settings, analysis records, findings, verdicts, notifications, synchronization state. Use migrations.

### Qdrant
Historical incident embeddings and metadata. Only for semantic incident retrieval, not primary transactional state.

## 4. Real Product Features

### Phase 1 — GitHub Identity
1. GitHub sign-in.
2. OAuth/GitHub App permission flow.
3. Repository selection.
4. Secure backend authorization.
5. View/update/revoke permissions.
6. No manual PAT entry for normal users.

### Phase 2 — Synchronization
7. Repository, branch, PR, commit, review, workflow synchronization.
8. GitHub webhooks.
9. Scheduled background synchronization.
10. Last-sync timestamp and error reporting.

### Phase 3 — Dashboard
11. Repository list/cards.
12. Safety score.
13. Safe/warning/blocked status.
14. Open PRs.
15. Recent activity.
16. Latest analysis time.
17. Filters.
18. Safety trend chart.

### Phase 4 — Repository Workspace
19. Branches, PRs, commits, workflows.
20. Deployment confidence.
21. Four-agent findings.
22. Severity, explanation, affected files, recommendations.
23. GitHub PR/commit links.

### Phase 5 — Activity & Notifications
24. Unified activity timeline.
25. Event filters/details.
26. In-app notifications for blocked PRs, critical findings, major score changes, workflow failures, relevant incidents.

### Phase 6 — Analytics
27. Safety history.
28. Recurring risks.
29. Incident frequency.
30. Verification gaps.
31. Blocked PR trends.
32. Weekly/monthly reports and period comparisons.

### Phase 7 — Visualization
33. Simple branch/commit graph.
34. Commit → files → PR → findings navigation.
35. Risk/incident introduction points.

## 5. Implementation Order
1. GitHub identity/authorization
2. Repository/PR synchronization
3. Secure core analysis pipeline
4. Agent evaluation + deterministic verdict
5. Dashboard
6. Repository workspace + findings
7. Activity timeline
8. Notifications
9. Qdrant incident memory
10. Branch/commit graph
11. Long-term analytics

## 6. Security
Mandatory: least privilege, backend-only credentials, encryption, webhook HMAC verification, strict authorization/tenant isolation, restricted CORS, input validation, SSRF protection, prompt-injection defenses, secret redaction, dependency scanning, security headers, rate limiting where appropriate, safe audit logging, and no arbitrary repository-code execution in normal analysis.

## 7. Cleanup
After verification, remove duplicate verdict logic, obsolete Prism references, disconnected Foundry paths, unfinished Azure Function/MCP scaffolding if out of scope, dead configuration, stale startup/docs, and unused dependencies/env vars. Confirm before deleting ambiguous code.
