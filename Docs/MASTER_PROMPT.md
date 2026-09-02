# SafeLane — Master Implementation Prompt

## Mission
You are the principal engineer transforming the current SafeLane repository into a production-grade, secure GitHub PR risk-analysis platform.

You are working in Emergent with no prior conversation context. Read these files completely before changing code:

1. `MASTER_PROMPT.md` — execution rules.
2. `INSTRUCTIONS_TASKS.md` — concrete problems, target architecture, implementation backlog.
3. `CONTEXT.md` — product intent, scope, and production goals.

Then inspect the repository itself. The repository is the implementation source of truth; these files define the intended target.

## Execution Strategy
Do not blindly rewrite the project.

1. Inspect repository structure, runtime, dependencies, APIs, data flow, and integrations.
2. Compare implementation with `INSTRUCTIONS_TASKS.md`.
3. Build a dependency-aware plan.
4. Use focused subagents for architecture, security, backend/agents, frontend, and infrastructure.
5. Integrate all work centrally.
6. Run tests, build, static checks, security checks, and integration checks.
7. Perform a second end-to-end architecture review.
8. Remove confirmed dead/legacy code.
9. Update documentation after implementation is verified.

## Subagents
Use subagents deliberately:

- **Architecture:** map modules, APIs, dependencies, data flows, and integration risks.
- **Security:** audit OAuth/GitHub permissions, secrets, JWT/session handling, webhook verification, authorization, SSRF, injection, CORS, logs, dependencies, tenant isolation.
- **Backend/Agents:** implement ingestion, orchestrator, four agents, evaluator, retries, budgets, deterministic verdict/policy, publishing.
- **Frontend:** GitHub sign-in, repository sync UI, dashboard, repository workspace, timeline, findings, notifications, trends/graphs.
- **Data/Infrastructure:** PostgreSQL, migrations, Qdrant, background jobs, synchronization, configuration, deployment, observability.

Do not assume subagent work integrates correctly. Review the combined result and resolve interface/contract mismatches.

## Integration-First Rule
Trace every feature end-to-end:

`UI/GitHub Event → API/Ingestion → Service → Orchestrator → Agent/Deterministic Module → Evaluator → Policy/Verdict → DB/Knowledge → UI/GitHub`

A feature is complete only when its caller, callee, contract, configuration, authentication, persistence, error handling, and user-visible result all work together.

## Agent Safety
No agent may run indefinitely.

Enforce:
- execution timeout
- token/model budget
- iteration limit
- bounded retries
- cancellation
- structured outputs

Flow:

`Agent → Schema/Evidence Evaluation → Accept`
or
`Agent → Targeted Feedback → Retry (max 2–3) → insufficient_analysis`

Never invent missing evidence.

## Security
Treat security as a first-class requirement:
- GitHub OAuth/GitHub App with least privilege
- backend-only credential handling
- encryption at rest
- no raw tokens in browser/JWT/logs
- signed webhook verification
- strict authorization and tenant isolation
- restricted CORS
- input validation
- SSRF protection
- prompt-injection defenses for untrusted repository content
- safe GitHub API access
- secret redaction
- dependency/security scanning
- no arbitrary repository-code execution unless explicitly sandboxed

Keep deterministic Security Preflight; AI must not replace hard security controls.

## Dead/Legacy Code
Remove only code confirmed to be:
- unreachable
- duplicated
- obsolete
- outside the finalized product scope
- inherited and unnecessary

Verify before deletion. Known candidates from the audit include disconnected MCP/Azure Function scaffolding, stale Prism references, duplicate verdict logic, and dead configuration.

## Verification
After each major phase run:
- unit tests
- integration tests
- lint/type checks
- dependency/security scans
- build
- migration checks
- API contract checks
- auth/authorization tests
- frontend/backend integration tests

Final review must check for broken routes/imports, orphan services, insecure configuration, silent failures, unbounded agent loops, credential exposure, missing migrations, and UI-only mocks.

## Definition of Done
Do not claim completion until:
1. Target architecture is implemented.
2. Major audit findings are fixed or explicitly documented.
3. GitHub authorization and repository access work without manual PAT entry for normal users.
4. Webhook + scheduled synchronization work.
5. Four agents have clear contracts and run through the orchestrator.
6. Outputs are evaluated and retries are bounded.
7. Security Preflight and deterministic policy remain authoritative.
8. One canonical verdict engine exists.
9. PostgreSQL is the durable store.
10. Qdrant is the incident-memory store.
11. Dashboard/workspace use real backend data.
12. Security checks pass.
13. Tests and build pass.
14. Confirmed dead/legacy code is removed safely.
15. Documentation matches actual behavior.

Completion must be evidenced by tests, builds, static analysis, security checks, and integration verification.
