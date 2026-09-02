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

SafeLane fills a critical operational gap. It acts as an automated, objective change reviewer that protects engineering teams from high-risk, silent regressions like deleted `@retry` decorators, unsafe SQL migrations, missing tests, or calendar hazards (Friday 5 PM deploys).

</div>

---

## 🚀 Quickstart

SafeLane v2 is built as a unified platform containing both the FastAPI engine and React SPA.

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

Detailed documentation has been split into focused domains:

| Document | Description |
| :--- | :--- |
| **[Product Overview](Docs/product.md)** | The "Why" and "How": SafeLane's philosophy, the five core pillars, and UI/UX experience. |
| **[Technical Design](Docs/technical-design.md)** | System architecture, end-to-end orchestration flow, invariants, and testing matrix. |
| **[Operations & Setup](Docs/operations.md)** | Step-by-step setup guides, GitHub OAuth configuration, and local webhook simulation. |
| **[Roadmap](Docs/roadmap.md)** | Planned features, PAT support integration, and future expansion paths. |

---

<div align="center">

**SafeLane v2** — *Engineered with precision for safer software delivery.*  
Made with ❤️ for GitHub developers and engineering reliability teams.

</div>
