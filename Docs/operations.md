# Operations & Getting Started: SafeLane v2

## ⚡ Interactive Walkthrough & Getting Started

### 1. Prerequisites & 1-Minute Setup

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

### 2. GitHub OAuth App Configuration

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

### 3. Running the Unified Server & Dashboard

Start the single unified FastAPI service (which serves both the API and the compiled React SPA):

```bash
# Start backend server on port 8000
uvicorn platform_app.server.app:app --reload --port 8000
```

- 🌐 **Web Dashboard & Onboarding**: Open [`http://localhost:8000`](http://localhost:8000) in your browser.
- 🩺 **Health Check**: [`http://localhost:8000/health`](http://localhost:8000/health)
- 📖 **Interactive API Documentation**: [`http://localhost:8000/docs`](http://localhost:8000/docs)

*(For frontend active development with Hot Module Replacement, run `cd platform_app/frontend && npm run dev` on port 5173).*

### 4. Simulating Webhooks & Test Suite Execution

Run the complete 107+ test suite to verify the entire system:

```bash
# Run all tests
python -m pytest tests/ -v
```

**Simulate a Pull Request Webhook via cURL:**

```bash
curl -X POST "http://localhost:8000/webhook/github" \
     -H "Content-Type: application/json" \
     -d '{
       "action": "opened",
       "pull_request": {
         "number": 101,
         "head": {"sha": "a1b2c3d4e5f6"}
       },
       "repository": {
         "full_name": "acme/payment-service"
       }
     }'
```
