# 🧠 ChaosLab – Safe Chaos Engineering with E2B + Groq + Grafana MCP

> Run controlled chaos experiments in ephemeral E2B sandboxes, analyze with Groq AI, and visualize system resilience in Grafana MCP.

---

## 📦 Overview

ChaosLab enables developers to test how their applications behave under *realistic failure scenarios* — network latency, dependency outage, memory pressure, disk fill, etc.  
Experiments run in **isolated E2B sandboxes**, analyzed by **Groq AI**, and results are visualized through **Grafana MCP dashboards**.

---

## ⚙️ Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | **React + TypeScript + Vite** |
| Backend | **FastAPI (Python)** |
| Runtime | **E2B Cloud Sandboxes** |
| AI Analysis | **Groq (Mixtral 8x7B)** |
| Metrics & Visualization | **Grafana MCP** |

---

## 🧩 Updated System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ChaosLab Application                  │
│  (Running locally or on a server)                       │
│                                                          │
│  ┌──────────────┐      ┌──────────────┐                │
│  │   Frontend   │─────▶│   FastAPI    │                │
│  │  React + TS  │      │   Backend    │                │
│  └──────────────┘      └──────┬───────┘                │
│                                │                         │
└────────────────────────────────┼─────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
         ┌──────────────┐  ┌─────────┐  ┌──────────┐
         │ E2B Sandbox  │  │  Groq   │  │ Grafana  │
         │              │  │   AI    │  │   MCP    │
         │ ┌──────────┐ │  │         │  │          │
         │ │ Flask    │ │  └─────────┘  └──────────┘
         │ │ Test App │ │       ▲            ▲
         │ └──────────┘ │       │            │
         │      +       │       │            │
         │ ┌──────────┐ │       │            │
         │ │  Chaos   │ │       │            │
         │ │ Scripts  │ │       │            │
         │ └──────────┘ │       │            │
         │      │       │       │            │
         │      ▼       │       │            │
         │   Logs &    │───────┘            │
         │   Metrics   │                    │
         └─────────────┘────────────────────┘
```

---

## 🔄 Workflow

### 1️⃣ **Experiment Start**
```
User clicks "Start Chaos Test"
  → Frontend calls: POST /api/experiment/start
  → FastAPI Backend:
      a) Spins up E2B sandbox
      b) Deploys pre-built Flask app into sandbox
      c) Runs chaos script (network delay, memory pressure, etc.)
      d) Collects logs/metrics from sandbox
```

### 2️⃣ **AI Analysis**
```
E2B sandbox generates logs & metrics
  → FastAPI receives data
  → Sends to Groq AI with structured prompt
  → Groq analyzes and returns:
      - Human-readable summary
      - Extracted metrics (CPU, memory, errors, recovery time)
      - Severity assessment
      - Actionable recommendations
```

### 3️⃣ **Visualization**
```
FastAPI calls Grafana MCP
  → Creates dashboard with metrics from Groq analysis
  → Returns dashboard URL to frontend
  → Frontend embeds Grafana iframe
```

---

## 👥 Implementation (Single Developer)

### 🧑‍💻 Backend / Infra
**Directory:** `/backend`

#### Responsibilities
- Set up FastAPI server
- Integrate with **E2B SDK**
- Orchestrate sandbox lifecycle:
  - Create sandbox
  - Deploy Flask test app
  - Run chaos injector script
  - Collect logs and system metrics
  - Destroy sandbox
- **Groq AI Integration**:
  - Send logs to Groq for analysis
  - Extract structured metrics
  - Generate summaries and recommendations
- Configure Grafana MCP connection
- Expose REST endpoints:
  - `POST /api/experiment/start`
  - `GET /api/experiment/:id/status`
  - `GET /api/experiment/:id/results`

#### Deliverables
- `main.py` (FastAPI entry)
- `services/e2b_manager.py`
- `services/groq_analyzer.py` ✨ **NEW**
- `services/grafana_client.py`
- `models.py` (Pydantic models)
- `requirements.txt`
- `.env.example` with API keys

---

### 🧑‍🎨 Frontend / UX
**Directory:** `/frontend`

#### Responsibilities
- Build React + TypeScript app with Vite
- Pages/components:
  - **ExperimentForm** – Select chaos scenario + configure
  - **ExperimentStatus** – Show progress with polling
  - **ResultsView** – Display AI summary, metrics, and Grafana dashboard
- Integrate with backend REST API
- Handle loading/error states
- Premium design system with modern aesthetics

#### Deliverables
- `/src/App.tsx` – main router & layout
- `/src/components/ExperimentForm.tsx`
- `/src/components/ExperimentStatus.tsx`
- `/src/components/ResultsView.tsx`
- `/src/api/client.ts` – API wrapper
- `/src/index.css` – Design system
- `.env.example` with `VITE_API_URL`

---

## 🧪 Supported Chaos Scenarios

| Name | Description | Expected Outcome |
|------|--------------|------------------|
| `network_delay` | Adds 300 ms latency using `tc qdisc` | Test client timeouts |
| `memory_pressure` | Fills 80% RAM gradually | Check graceful degradation |
| `disk_full` | Fill `/tmp` until near-full | Validate error logging |
| `process_kill` | Randomly kills main PID | Verify self-healing logic |
| `dependency_failure` | Mocks DNS/DB failure | Observe retries or crash |

---

## 📊 Groq AI Analysis

### Input to Groq
```
Scenario: network_delay
Duration: 60 seconds
Metrics:
  - CPU Usage: 85.5%
  - Memory Usage: 78.2%
  - Error Count: 12
Logs: [application logs...]
```

### Output from Groq
```json
{
  "summary": "App experienced 300ms latency, retried 3 times, recovered in 8s",
  "metrics": {
    "cpu_peak": 85.5,
    "memory_peak": 78.2,
    "error_count": 12,
    "recovery_time_seconds": 8.0,
    "latency_p95": 320.5
  },
  "severity": "medium",
  "recommendations": [
    "Implement exponential backoff",
    "Add circuit breaker pattern",
    "Monitor resource usage and set up alerts"
  ]
}
```

---

## 🔑 Environment Variables

### Unified `.env` File
```bash
# E2B Configuration
E2B_API_KEY=your_e2b_api_key

# Groq Configuration
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=mixtral-8x7b-32768

# Grafana MCP Configuration
GRAFANA_MCP_URL=http://localhost:3000
GRAFANA_MCP_TOKEN=your_grafana_token

# Backend Configuration
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0

# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

---

## 🧰 Dependencies Summary

### Backend
- `fastapi`
- `uvicorn`
- `e2b`
- `groq` ✨ **NEW**
- `requests`
- `pydantic`
- `python-dotenv`

### Frontend
- `react`, `react-dom`
- `typescript`
- `vite`
- `axios`
- `lucide-react` (icons)

---

## 🏁 Demo Script (for judges)

1. Launch app at `http://localhost:5173`
2. Select chaos scenario: **Network Delay**
3. Configure duration (60s) and intensity (medium)
4. Start experiment → E2B spins up sandbox
5. Watch progress bar and status updates
6. View AI-generated summary:
   > "App handled delay gracefully with 3 retries and recovered within 8s."
7. See extracted metrics: CPU 85%, Memory 78%, 12 errors
8. View embedded Grafana dashboard with visualizations
9. Review AI recommendations for improving resilience

---

## 🚀 Quick Start

### Installation
```bash
# 1. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 2. Install backend
cd backend
pip install -r requirements.txt

# 3. Install frontend
cd ../frontend
npm install
```

### Running
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser!

---

**Goal:** Show that ChaosLab gives developers *AI-powered visibility* into resilience through safe, visual experiments using E2B + Groq + Grafana MCP.


---

## 📦 Overview

ChaosLab enables developers to test how their applications behave under *realistic failure scenarios* — network latency, dependency outage, memory pressure, disk fill, etc.  
Experiments run in **isolated E2B sandboxes**, and results are visualized through **Grafana MCP dashboards** from Docker Hub Marketplace.

---

## ⚙️ Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | **React + TypeScript + Vite** (or Next.js if preferred) |
| Backend | **FastAPI (Python)** |
| Runtime | **E2B Cloud Sandboxes** |
| Metrics & Visualization | **Grafana MCP (from Docker Hub)** |
| Optional Storage | Postgres MCP (for saving experiment history) |

---

## 🧩 System Architecture

```
Frontend (React/TS)
   │
   ▼
Backend API (FastAPI)
   │  ├─ Orchestrates E2B runs
   │  ├─ Connects to Grafana MCP
   │  └─ Stores experiment data
   ▼
E2B Sandbox
   ├─ Runs user app (Docker image)
   ├─ Injects chaos scripts
   └─ Exposes metrics to Grafana MCP
```

---

## 👥 Team Responsibilities

### 🧑‍💻 You – **Backend / Infra Lead**
**Directory:** `/backend`

#### Responsibilities
- Set up FastAPI server
- Integrate with **E2B SDK**
- Orchestrate sandbox lifecycle:
  - Create sandbox
  - Pull Docker image (via Docker CLI inside E2B)
  - Run app container
  - Run chaos injector script
  - Stream metrics to Grafana MCP
  - Destroy sandbox
- Expose REST endpoints:
  - `POST /experiment/start`
  - `GET /experiment/:id/status`
  - `GET /experiment/:id/results`
- Configure Grafana MCP connection (datasource + dashboard)
- Generate experiment summaries
- (Optional) Store logs/results in Postgres MCP

#### Deliverables
- `main.py` (FastAPI entry)
- `services/e2b_manager.py`
- `services/grafana_client.py`
- `scripts/chaos/` (individual chaos scripts)
- `requirements.txt` / `pyproject.toml`
- `.env.example` with API keys for E2B and Grafana MCP
- Example request JSON for frontend integration

#### Example Endpoint Spec

```python
POST /experiment/start
{
  "image": "docker.io/library/flask-app:latest",
  "scenario": "network_delay"
}
→ returns { "experiment_id": "abc123", "grafana_url": "..." }
```

---

### 🧑‍🎨 Teammate – **Frontend / UX Lead**
**Directory:** `/frontend`

#### Responsibilities
- Build React + TypeScript app (use Vite or Next.js)
- Pages/components:
  - **Home** – Select Docker image + chaos scenario
  - **RunView** – Show experiment progress
  - **Dashboard** – Embed Grafana iframe (live metrics)
  - **Results** – Display AI summary & logs
- Integrate with backend REST API
- Handle loading/error states
- Add minimal design system (Tailwind)
- Make it demo-friendly for hackathon presentation

#### Deliverables
- `/src/App.tsx` – main router & layout
- `/src/components/ExperimentForm.tsx`
- `/src/components/ExperimentDashboard.tsx`
- `/src/components/ResultCard.tsx`
- `/src/api/client.ts` – axios/fetch wrapper
- `.env.example` with `VITE_API_URL`
- Optional: `iframe` wrapper for Grafana MCP dashboard

#### Example Flow
1. User inputs Docker image + selects chaos type.
2. Frontend calls `POST /experiment/start`.
3. Backend returns Grafana URL → embed via `<iframe>`.
4. When experiment ends, call `GET /experiment/:id/results` and render summary.

---

## 🧪 Supported Chaos Scenarios

| Name | Description | Expected Outcome |
|------|--------------|------------------|
| `network_delay` | Adds 300 ms latency using `tc qdisc` | Test client timeouts |
| `dependency_failure` | Mocks DNS/DB failure | Observe retries or crash |
| `memory_pressure` | Fills 80 % RAM gradually | Check graceful degradation |
| `disk_full` | Fill `/tmp` until near-full | Validate error logging |
| `process_kill` | Randomly kills main PID | Verify self-healing logic |

---

## 📊 Grafana MCP Setup

1. Deploy **Grafana MCP** from Docker Hub Marketplace.
2. Add Prometheus datasource (either local or MCP).
3. Create `ChaosLab` dashboard with:
   - CPU usage
   - Memory
   - Error rate
   - Response latency
4. Copy share link and use it for the iframe in frontend.
5. Store API key/URL in backend `.env`.

---

## 🕒 Suggested Timeline (6-hour build)

| Time | Backend | Frontend |
|------|----------|-----------|
| 0–1h | Scaffold FastAPI project | Setup React + Tailwind |
| 1–2h | Integrate E2B sandbox | Build experiment form |
| 2–3h | Implement chaos scripts | Create dashboard view |
| 3–4h | Connect Grafana MCP | Embed Grafana iframe |
| 4–5h | Add `/results` endpoint | Add result summary UI |
| 5–6h | Polish, test, record demo | Polish UI + prep demo flow |

---

## 🔑 Environment Variables

### Backend
```
E2B_API_KEY=
GRAFANA_MCP_URL=
GRAFANA_MCP_TOKEN=
POSTGRES_URL= (optional)
```

### Frontend
```
VITE_API_URL=http://localhost:8000
GRAFANA_EMBED_URL=<iframe URL>
```

---

## 🧰 Dependencies Summary

### Backend
- `fastapi`
- `uvicorn`
- `requests`
- `e2b`
- `docker` (CLI in sandbox)
- `prometheus-client`
- `python-dotenv`

### Frontend
- `react`, `react-dom`
- `typescript`
- `vite` or `next`
- `axios`
- `tailwindcss`
- `lucide-react` (icons)

---

## 🏁 Demo Script (for judges)
1. Launch app.
2. Input Docker image (e.g., `chaoslab-demo/flask-api`).
3. Choose chaos scenario: **Network Delay**.
4. Start experiment → E2B spins up sandbox.
5. Grafana dashboard appears live (CPU spikes, latency graphs).
6. Show summary card:
   > “App handled delay gracefully with 2 retries and recovered within 8 s.”

---

**Goal:** Show that ChaosLab gives developers *visibility* into resilience through safe, visual experiments using E2B + Grafana MCP.
