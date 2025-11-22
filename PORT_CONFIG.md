# 🔧 Port Configuration for ChaosLab

## Current Setup

You have the following containers running:

| Service | Port | URL |
|---------|------|-----|
| **Grafana MCP** | 8000 | http://localhost:8000 |
| **Grafana** | 3000 | http://localhost:3000 |
| **ChaosLab Backend** | 8001 | http://localhost:8001 |
| **ChaosLab Frontend** | 5173 | http://localhost:5173 |

## Configuration Files Updated

### 1. `.env.example` and `.env`
```bash
# Grafana MCP (your existing container)
GRAFANA_MCP_URL=http://localhost:8000
GRAFANA_MCP_TOKEN=your_grafana_mcp_token_here

# Backend (changed from 8000 to 8001)
BACKEND_PORT=8001
VITE_API_URL=http://localhost:8001
```

### 2. `backend/main.py`
- Default backend port: **8001**
- Default Grafana MCP URL: **http://localhost:8000**

### 3. `frontend/vite.config.ts`
- API proxy target: **http://localhost:8001**

## How to Run

### 1. Update Your .env File

```bash
cd /Users/satheesh/e2b_docker

# Copy the example
cp .env.example .env

# Edit .env and set:
E2B_API_KEY=your_e2b_key
GROQ_API_KEY=your_groq_key
GRAFANA_MCP_URL=http://localhost:8000
GRAFANA_MCP_TOKEN=your_actual_grafana_mcp_token
```

### 2. Start Backend

```bash
cd backend
python main.py

# Backend will run on http://localhost:8001
```

### 3. Start Frontend

```bash
cd frontend
npm run dev

# Frontend will run on http://localhost:5173
```

### 4. Access the App

Open your browser: **http://localhost:5173**

## Grafana MCP Integration

Your Grafana MCP container on port 8000 should have:
- API endpoint for creating dashboards
- Token authentication configured

The backend will call:
```
POST http://localhost:8000/api/dashboards/db
Authorization: Bearer YOUR_TOKEN
```

## Troubleshooting

### Port Already in Use

If you see "Address already in use" errors:

```bash
# Check what's using a port
lsof -i :8001  # Backend
lsof -i :5173  # Frontend
lsof -i :8000  # Grafana MCP

# Kill a process if needed
kill -9 <PID>
```

### Backend Can't Connect to Grafana MCP

```bash
# Test Grafana MCP is accessible
curl http://localhost:8000/api/health

# Check if token is valid
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/org
```

### Frontend Can't Connect to Backend

```bash
# Check backend is running
curl http://localhost:8001/

# Should return:
# {"service":"ChaosLab API","status":"healthy","version":"1.0.0"}
```

## Quick Test

After starting everything:

```bash
# 1. Test backend health
curl http://localhost:8001/

# 2. Open frontend
open http://localhost:5173

# 3. Run a quick experiment
# - Select "Network Delay"
# - Click "Start Chaos Experiment"
# - Watch the magic happen!
```

## Summary

✅ **Grafana MCP**: Port 8000 (your existing container)  
✅ **Backend**: Port 8001 (no conflict)  
✅ **Frontend**: Port 5173 (default Vite)  
✅ **All configs updated** to use these ports

You're all set! 🚀
