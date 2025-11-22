# 🧠 ChaosLab

> Safe chaos engineering with E2B sandboxes, Groq AI analysis, and Grafana MCP visualization

Test your application's resilience by running controlled chaos experiments in isolated environments, with AI-powered insights and beautiful dashboards.

---

## 🎯 What is ChaosLab?

ChaosLab enables developers to test how their applications behave under realistic failure scenarios:
- **Network latency** - Test timeout handling
- **Memory pressure** - Validate resource management
- **Disk full** - Check error handling
- **Process crashes** - Verify recovery mechanisms
- **Dependency failures** - Test resilience patterns

All experiments run in **isolated E2B sandboxes**, analyzed by **Groq AI**, and visualized through **Grafana MCP dashboards**.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ChaosLab Application                  │
│                                                          │
│  Frontend (React + TS) ──▶ Backend (FastAPI)           │
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
         │ │ Test App │ │  └─────────┘  └──────────┘
         │ └──────────┘ │       ▲            ▲
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

### Workflow

1. **User configures experiment** via React frontend
2. **FastAPI backend** creates E2B sandbox
3. **Test Flask app** deployed in sandbox
4. **Chaos script** injects failures
5. **Logs & metrics** collected from sandbox
6. **Groq AI** analyzes results and extracts insights
7. **Grafana MCP** creates dashboard
8. **Results displayed** with AI summary + embedded dashboard

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.10+ (for backend)
- **E2B API Key** - [Get one here](https://e2b.dev)
- **Groq API Key** - [Get one here](https://console.groq.com)
- **Grafana Instance** (optional for full dashboard support)

### Installation

1. **Clone the repository**
   ```bash
   cd e2b_docker
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

1. **Start the backend** (in `backend/` directory)
   ```bash
   python main.py
   # Or with uvicorn:
   uvicorn main:app --reload
   ```
   Backend will run on `http://localhost:8001`

2. **Start the frontend** (in `frontend/` directory)
   ```bash
   npm run dev
   ```
   Frontend will run on `http://localhost:5173`

3. **Open your browser**
   Navigate to `http://localhost:5173`

---

## 📦 Project Structure

```
e2b_docker/
├── .env                          # Environment configuration
├── .env.example                  # Template for environment variables
├── README.md                     # This file
├── REQUIREMENTS.md               # Original requirements
├── ARCHITECTURE.md               # Detailed architecture docs
│
├── backend/                      # FastAPI backend
│   ├── main.py                   # Application entry point
│   ├── models.py                 # Pydantic models
│   ├── requirements.txt          # Python dependencies
│   └── services/
│       ├── e2b_manager.py       # E2B sandbox orchestration
│       ├── groq_analyzer.py     # Groq AI integration
│       └── grafana_client.py    # Grafana MCP client
│
└── frontend/                     # React frontend
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx              # Main application
        ├── index.css            # Design system
        ├── api/
        │   └── client.ts        # Backend API client
        └── components/
            ├── ExperimentForm.tsx
            ├── ExperimentStatus.tsx
            └── ResultsView.tsx
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```bash
# E2B Configuration
E2B_API_KEY=your_e2b_api_key_here

# Groq Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=mixtral-8x7b-32768

# Grafana MCP Configuration
GRAFANA_MCP_URL=http://localhost:3000
GRAFANA_MCP_TOKEN=your_grafana_token_here

# Backend Configuration
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0

# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Available Chaos Scenarios

| Scenario | Description | What It Tests |
|----------|-------------|---------------|
| **Network Delay** | Adds 300ms latency | Timeout handling, retry logic |
| **Memory Pressure** | Fills 80% RAM | Resource management, graceful degradation |
| **Disk Full** | Fills `/tmp` directory | Error logging, disk space handling |
| **Process Kill** | Randomly terminates processes | Self-healing, recovery mechanisms |
| **Dependency Failure** | Mocks DNS/DB failures | Circuit breakers, fallback patterns |

---

## 📊 API Endpoints

### `POST /api/experiment/start`
Start a new chaos experiment

**Request:**
```json
{
  "scenario": "network_delay",
  "config": {
    "duration": 60,
    "intensity": "medium"
  }
}
```

**Response:**
```json
{
  "experiment_id": "exp_abc123",
  "status": "running",
  "created_at": "2025-11-22T12:00:00Z"
}
```

### `GET /api/experiment/{id}/status`
Get current experiment status

**Response:**
```json
{
  "experiment_id": "exp_abc123",
  "status": "analyzing",
  "progress": 75,
  "message": null
}
```

### `GET /api/experiment/{id}/results`
Get complete experiment results

**Response:**
```json
{
  "experiment_id": "exp_abc123",
  "summary": "App experienced 300ms latency, retried 3 times, recovered in 8s",
  "metrics": {
    "cpu_peak": 85.5,
    "memory_peak": 78.2,
    "error_count": 12,
    "recovery_time_seconds": 8.0
  },
  "grafana_url": "https://grafana.../dashboard/...",
  "recommendations": [
    "Implement exponential backoff",
    "Add circuit breaker pattern"
  ],
  "severity": "medium"
}
```

---

## 🎨 Features

### ✨ Beautiful UI
- Premium dark theme with gradients
- Smooth animations and transitions
- Responsive design
- Real-time progress tracking

### 🤖 AI-Powered Analysis
- Groq AI analyzes experiment logs
- Extracts structured metrics
- Generates human-readable summaries
- Provides actionable recommendations

### 📈 Grafana Dashboards
- Automatic dashboard creation
- Real-time metrics visualization
- Embedded iframe support
- Shareable dashboard URLs

### 🔒 Safe Execution
- Isolated E2B sandboxes
- Automatic cleanup
- No impact on production
- Reproducible experiments

---

## 🎬 Demo Script (for Hackathon)

1. **Launch the app** at `http://localhost:5173`
2. **Select chaos scenario**: "Network Delay"
3. **Configure**:
   - Duration: 60 seconds
   - Intensity: Medium
4. **Start experiment** → Watch E2B sandbox spin up
5. **View progress** → Real-time status updates
6. **See results**:
   - AI summary: "App handled delay gracefully with 3 retries, recovered in 8s"
   - Metrics: CPU 85%, Memory 78%, 12 errors
   - Grafana dashboard with visualizations
   - Recommendations for improvement

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + TypeScript + Vite |
| Styling | Vanilla CSS (Premium Design System) |
| Backend | FastAPI (Python) |
| Sandbox | E2B Cloud Sandboxes |
| AI Analysis | Groq (Mixtral 8x7B) |
| Visualization | Grafana MCP |
| Icons | Lucide React |

---

## 🐛 Troubleshooting

### Backend won't start
- Check that all environment variables are set in `.env`
- Verify Python dependencies are installed: `pip install -r requirements.txt`
- Ensure port 8000 is not in use

### Frontend won't start
- Check Node.js version (18+)
- Install dependencies: `npm install`
- Ensure port 5173 is not in use

### E2B sandbox errors
- Verify E2B API key is valid
- Check E2B account has available credits
- Review backend logs for detailed error messages

### Groq API errors
- Verify Groq API key is valid
- Check rate limits on your Groq account
- Ensure model name is correct in `.env`

---

## 📝 License

MIT License - feel free to use this for your hackathon and beyond!

---

## 🙏 Acknowledgments

Built with:
- [E2B](https://e2b.dev) - Cloud sandboxes
- [Groq](https://groq.com) - Fast AI inference
- [Grafana](https://grafana.com) - Metrics visualization
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [React](https://react.dev) - UI framework
- [Vite](https://vitejs.dev) - Build tool

---

**Happy Chaos Engineering! 🧠⚡**
