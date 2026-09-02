# SafeLane — Production Context

## Product
SafeLane is an enterprise-oriented AI-assisted GitHub PR safety and risk-analysis platform.

It helps engineering teams identify security, reliability, verification, incident-history, and release-context risks before code is merged or released.

SafeLane combines AI reasoning with evidence validation and deterministic security/policy controls. It assists engineers; it does not replace deterministic security policy.

## Core Goal
For each relevant pull request:

```text
GitHub PR
  ↓
Trusted change/repository context
  ↓
Four specialized analyses
  ↓
Evidence evaluation
  ↓
Deterministic security/policy
  ↓
Explainable verdict
  ↓
Dashboard + GitHub
```

The system should be secure, explainable, observable, bounded in AI execution, resilient to partial failure, maintainable, and production deployable.

## Primary Users
Developers, engineering teams, security/reliability teams, and engineering managers who need repository and PR risk visibility.

## Main Capabilities

### GitHub Connection
Users sign in with GitHub and authorize selected repositories through OAuth or a GitHub App. Authorization is stored securely on the backend, permissions can be reviewed/changed/revoked, and normal users do not paste PATs.

### Synchronization
SafeLane synchronizes repositories, branches, PRs, commits, reviews, and workflow runs using webhooks plus scheduled background updates. The UI shows sync time and connection errors.

### PR Risk Analysis
- **Change Intelligence** — change/risk analysis.
- **Incident Memory** — historical incident retrieval.
- **Verification Readiness** — testing/verification adequacy.
- **Release Context** — operational/deployment context.

An **Orchestrator Agent** coordinates them. A **Control/Evaluation Layer** validates outputs and enforces execution limits. A deterministic **Security Preflight + Verdict/Policy Engine** is authoritative.

### Dashboard
Show connected repositories, safety score, safe/warning/blocked state, open PRs, recent activity, latest analysis, filters, and safety trends.

### Repository Workspace
Show branches, PRs, commits, workflows, deployment confidence, four-agent findings, severity, explanations, affected files, recommendations, and GitHub links.

### Activity & Notifications
Timeline for commits, PRs, reviews, workflows, analyses, incidents, and score changes. Start with in-app notifications for blocked PRs, critical findings, major score changes, workflow failures, and relevant incidents.

### Long-Term Analytics
Track safety trends, recurring risks, incident frequency, verification gaps, blocked PRs, and weekly/monthly repository health.

## Technology Responsibilities
**GitHub:** source and event platform  
**FastAPI:** API/ingestion boundary  
**Azure AI Foundry:** agent/model runtime  
**PostgreSQL:** transactional application state  
**Qdrant:** semantic incident-memory retrieval  
**Frontend:** dashboard/workspace/timeline/notifications/analytics

## Reliability
Every agent has a timeout, model/token budget, iteration limit, and retry limit. Failed analysis becomes an explicit failure or `INSUFFICIENT_ANALYSIS` state. The system must never fabricate evidence or silently convert missing data into a confident result.

## Security
Use least privilege, backend-only credential handling, encryption, verified webhooks, strict authorization and tenant isolation, input validation, SSRF protection, secret redaction, secure CORS, security/dependency scanning, and defenses against prompt injection from repository content. Deterministic security policy remains authoritative.

## Product Boundary
SafeLane is a GitHub engineering safety and PR risk platform. Do not restore inherited or unfinished features simply because they exist in the old repository. Prefer a smaller set of integrated, production-quality capabilities over disconnected demos.
