<div align="center">

# 🛡️ SafeLane v2.3
### *The Autonomous Change Assurance Fabric & Pre-Deployment Risk Gate for GitHub*

[![Version](https://img.shields.io/badge/Version-2.3.0-6366F1?style=for-the-badge)](pyproject.toml)
[![Tests](https://img.shields.io/badge/Tests-110%2F110%20Passed-10B981?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Unified%20Gateway-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Tailwind-61DAFB?style=for-the-badge&logo=react&logoColor=black)](platform_app/frontend/)
[![OAuth](https://img.shields.io/badge/GitHub-OAuth%202.0%20PKCE-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

<br/>

> **"Tests pass" is not the same as "safe to ship."**  
> SafeLane v2 reads every GitHub pull request like a principal site reliability engineer — synthesizing deterministic security preflights, multi-agent evidence modules, calendar heuristics, and historical incident memory into a single mathematical **Deployment Confidence Score (0–100)** with actionable rollback playbooks and Copilot test nudges posted directly to the PR.

<br/>

SafeLane fills a critical operational gap. It acts as an automated, objective change reviewer that protects engineering teams from high-risk, silent regressions like deleted `@retry` decorators, unsafe SQL migrations, missing tests, or calendar hazards (Friday 5 PM deploys).

</div>

---

## 🏛️ Architectural Pillars

SafeLane is built upon five strict engineering pillars:

1. **Deterministic Security Preflight Overrides AI**: Zero-cost static regex and AST preflight scanning for credentials, unpinned actions, and command injections before AI dispatch.
2. **Multi-Angle Parallel Evidence Synthesis**: Four concurrent evidence dimensions evaluated in parallel (`Change Intelligence`, `Incident Memory`, `Verification Readiness`, `Release Context`).
3. **Strict Mathematical Scoring & Invariant Enforcement**: Base scoring with weighted deductions and security penalties:
   - Score $\ge 70$ and 0 Critical Findings $\implies$ `GREENLIGHT`
   - Score $< 70$ or $\ge 1$ Critical Finding $\implies$ `BLOCKED`
4. **Zero Secret Exposure & Frictionless 1-Click Identity**: OAuth is the primary user login method and manual PAT access is internal-only. Features a 1-click GitHub OAuth 2.0 PKCE flow (S256 code challenge/verifier), encrypted credentials at rest, and secure cookie-based session JWTs.
5. **Actionable Remediation (Never Just Complain)**: Generates automated branch-based Git Rollback Playbooks when blocked and Copilot test generation prompts for uncovered logic.

---

## 🛡️ Input Sanitization & Boundaries

Untrusted pull request diffs and file paths pass through `safelane/fabric/inputs.py`:
- **Diff Limit**: Diff input is strictly bounded by `MAX_DIFF_CHARS = 100_000` (100,000 characters). Diffs exceeding this threshold are sanitized and truncated as a request/token budget boundary for LLM reasoning rather than arbitrarily penalized.
- **Path Length Limit**: File paths are bounded to `MAX_PATH_LENGTH = 500` characters.
- **Sanitization**: Null bytes (`\x00`) are stripped and unicode text is normalized to NFKC format.

---

## 📋 Automated Rollback Playbook

When a pull request is marked `BLOCKED`, SafeLane synthesizes a concrete, branch-based rollback playbook targeting the exact commit HEAD SHA to ensure safe, reproducible rollbacks without clobbering history:

```bash
git fetch origin
git checkout -b revert-risky-changes-<head_sha[:7]>
git revert --no-commit <head_sha>..HEAD
git commit -m 'Revert risky changes identified by SafeLane'
git push origin revert-risky-changes-<head_sha[:7]>
```

---

## 🚀 Quickstart

SafeLane is built as a unified platform containing both the FastAPI engine and React SPA.

```bash
# 1. Clone repository
git clone https://github.com/Vishal-047/safe-lane_demo.git
cd "SafeLane v2"

# 2. Setup Python virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies & configure env
pip install -r requirements.txt
cp .env.example .env

# 4. Run the platform
uvicorn platform_app.server.app:app --reload --port 8000
```

> **Note:** You will need to configure a GitHub OAuth App and update your `.env` to fully use the platform. See [Operations & Setup](Docs/operations.md) for detailed instructions.

---

## 📚 Documentation

Detailed documentation is available across focused domain guides:

| Document | Description |
| :--- | :--- |
| **[Product Overview](Docs/product.md)** | The "Why" and "How": SafeLane's philosophy, the five core pillars, and UI/UX experience. |
| **[Technical Design](Docs/technical-design.md)** | System architecture, end-to-end orchestration flow, invariants, and testing matrix. |
| **[Operations & Setup](Docs/operations.md)** | Step-by-step setup guides, GitHub OAuth configuration, and local webhook simulation. |
| **[Roadmap](Docs/roadmap.md)** | Planned features, PAT support integration, and future expansion paths. |

---

<div align="center">

**SafeLane v2.3** — *Engineered with precision for safer software delivery.*  
Made with ❤️ for GitHub developers and engineering reliability teams.

</div>
