# 🚀 ChaosLab - Quick Reference

## 📋 Project Summary
**ChaosLab** - Chaos engineering platform with E2B sandboxes, Groq AI analysis, and Grafana MCP visualization.

---

## 🏃 Quick Start Commands

### First Time Setup
```bash
# 1. Configure environment
cp .env.example .env
# Edit .env and add your API keys:
#   - E2B_API_KEY
#   - GROQ_API_KEY
#   - GRAFANA_MCP_URL (optional)
#   - GRAFANA_MCP_TOKEN (optional)

# 2. Run setup script
./setup.sh
```

### Running the App

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate
python main.py
# Backend runs on http://localhost:8001
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:5173
```

**Open Browser:**
```
http://localhost:5173
```

---

## 🔑 Required API Keys

### E2B (Required)
- Sign up: https://e2b.dev
- Get API key from dashboard
- Add to `.env`: `E2B_API_KEY=your_key_here`

### Groq (Required)
- Sign up: https://console.groq.com
- Get API key from settings
- Add to `.env`: `GROQ_API_KEY=your_key_here`

### Grafana MCP (Optional)
- If you have a Grafana instance:
  - `GRAFANA_MCP_URL=http://your-grafana-url`
  - `GRAFANA_MCP_TOKEN=your_token`
- If not, the app will generate mock dashboard URLs

---

## 📁 Project Structure

```
e2b_docker/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── models.py        # Data models
│   └── services/        # Core services
│       ├── e2b_manager.py
│       ├── groq_analyzer.py
│       └── grafana_client.py
│
├── frontend/            # React frontend
│   └── src/
│       ├── App.tsx
│       ├── components/
│       └── api/
│
└── docs/
    ├── README.md
    ├── ARCHITECTURE.md
    └── REQUIREMENTS.md
```

---

## 🧪 Chaos Scenarios

| Scenario | What It Does | Duration |
|----------|-------------|----------|
| **Network Delay** | Adds 300ms latency | 10-300s |
| **Memory Pressure** | Fills 80% RAM | 10-300s |
| **Disk Full** | Fills /tmp directory | 10-300s |
| **Process Kill** | Kills processes randomly | 10-300s |
| **Dependency Failure** | Mocks DNS/DB failures | 10-300s |

---

## 🔧 API Endpoints

### Start Experiment
```bash
POST http://localhost:8000/api/experiment/start
Content-Type: application/json

{
  "scenario": "network_delay",
  "config": {
    "duration": 60,
    "intensity": "medium"
  }
}
```

### Get Status
```bash
GET http://localhost:8000/api/experiment/{experiment_id}/status
```

### Get Results
```bash
GET http://localhost:8000/api/experiment/{experiment_id}/results
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.10+)
python3 --version

# Reinstall dependencies
cd backend
pip install -r requirements.txt

# Check if port 8000 is free
lsof -i :8000
```

### Frontend won't start
```bash
# Check Node version (need 18+)
node --version

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check if port 5173 is free
lsof -i :5173
```

### E2B Errors
- Verify API key is correct in `.env`
- Check E2B account has credits
- Review backend logs for details

### Groq Errors
- Verify API key is correct in `.env`
- Check rate limits on Groq account
- Ensure model name is correct

---

## 📊 Expected Flow

1. **User** → Selects scenario → Configures → Starts
2. **Backend** → Creates sandbox → Deploys app → Runs chaos
3. **E2B** → Executes → Collects logs → Returns metrics
4. **Groq** → Analyzes → Extracts insights → Returns summary
5. **Grafana** → Creates dashboard → Returns URL
6. **Frontend** → Displays results → Shows recommendations

**Total Time:** ~30-350 seconds (depending on duration)

---

## 🎯 Demo Script

### For Hackathon Judges (3 minutes)

**1. Introduction (30s)**
- "ChaosLab tests app resilience with controlled chaos"
- "E2B sandboxes + Groq AI + Grafana visualization"

**2. Live Demo (2m)**
- Open app
- Select "Network Delay" scenario
- Set duration to 60 seconds
- Click "Start Chaos Experiment"
- Show progress bar updating
- Display AI summary and metrics
- Highlight recommendations

**3. Tech Stack (30s)**
- React + TypeScript frontend
- FastAPI backend
- E2B for isolation
- Groq for AI analysis
- Grafana for visualization

---

## 📝 Key Files

### Backend
- [main.py](file:///Users/satheesh/e2b_docker/backend/main.py) - API endpoints
- [e2b_manager.py](file:///Users/satheesh/e2b_docker/backend/services/e2b_manager.py) - Sandbox management
- [groq_analyzer.py](file:///Users/satheesh/e2b_docker/backend/services/groq_analyzer.py) - AI analysis

### Frontend
- [App.tsx](file:///Users/satheesh/e2b_docker/frontend/src/App.tsx) - Main app
- [ExperimentForm.tsx](file:///Users/satheesh/e2b_docker/frontend/src/components/ExperimentForm.tsx) - Configuration
- [ResultsView.tsx](file:///Users/satheesh/e2b_docker/frontend/src/components/ResultsView.tsx) - Results display

### Documentation
- [README.md](file:///Users/satheesh/e2b_docker/README.md) - Full documentation
- [ARCHITECTURE.md](file:///Users/satheesh/e2b_docker/ARCHITECTURE.md) - Technical details

---

## ✅ Pre-Demo Checklist

- [ ] API keys configured in `.env`
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Tested one complete experiment
- [ ] Screenshots taken
- [ ] Demo script practiced
- [ ] Backup plan if live demo fails

---

## 🎨 Design Highlights

- **Dark theme** with purple-blue gradients
- **Smooth animations** on all interactions
- **Real-time progress** tracking
- **Premium aesthetics** with modern design
- **Responsive layout** for all screen sizes

---

## 🚀 Next Steps After Hackathon

1. **Add Database** - PostgreSQL for persistence
2. **Async Execution** - Celery for background jobs
3. **WebSockets** - Real-time updates
4. **Custom Images** - Let users test their own apps
5. **Scheduled Tests** - Automated chaos testing
6. **Alerts** - Slack/Discord notifications

---

## 📞 Support

- **E2B Docs**: https://e2b.dev/docs
- **Groq Docs**: https://console.groq.com/docs
- **Grafana Docs**: https://grafana.com/docs

---

**Good luck with your hackathon! 🎉**
