# 🎨 Grafana MCP Integration with LLM

## How It Works Now

Your ChaosLab now uses **Groq LLM** to create Grafana dashboards via your **Grafana MCP server**!

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  ChaosLab Backend (localhost:9000)                      │
│                                                          │
│  1. Run Experiment → Collect Metrics                    │
│  2. Groq Analyzes → Extract Insights                    │
│  3. Groq + MCP → Create Dashboard                       │
│     │                                                    │
│     │  Groq receives:                                   │
│     │  - Experiment ID                                  │
│     │  - Metrics (CPU, memory, errors, etc.)           │
│     │  - Scenario type                                  │
│     │  - AI analysis summary                            │
│     │                                                    │
│     ▼                                                    │
│  ┌─────────────────────────────────┐                   │
│  │  Groq LLM                       │                   │
│  │  "Create a Grafana dashboard    │                   │
│  │   for this chaos experiment..." │                   │
│  └────────────┬────────────────────┘                   │
│               │                                          │
│               │ Uses MCP Protocol                        │
│               ▼                                          │
│  ┌─────────────────────────────────┐                   │
│  │  Grafana MCP Server             │                   │
│  │  localhost:8000                 │                   │
│  │  - Creates dashboard            │                   │
│  │  - Adds panels                  │                   │
│  │  - Returns URL                  │                   │
│  └─────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

### What the LLM Does

The Groq LLM receives a prompt like:

```
Create a Grafana dashboard for this chaos engineering experiment:

**Experiment ID:** exp_abc123
**Scenario:** network_delay
**Summary:** Application handled network delay gracefully with 
minimal impact...

**Metrics to visualize:**
{
  "cpu_peak": 45.2,
  "memory_peak": 62.8,
  "error_count": 3,
  "recovery_time_seconds": 8.5
}

**Dashboard Requirements:**
1. Title: "Chaos Experiment: network_delay - exp_abc123"
2. Panels needed:
   - CPU Usage (gauge) - show peak: 45.2%
   - Memory Usage (gauge) - show peak: 62.8%
   - Error Count (stat panel) - show: 3 errors
   - Recovery Time (stat panel) - show: 8.5s

**MCP Server:** http://localhost:8000

Create this dashboard and return the dashboard URL.
```

The LLM then:
1. Understands the requirements
2. Uses the MCP protocol to interact with your Grafana server
3. Creates appropriate panels and visualizations
4. Returns the dashboard URL

### Code Changes

**New File:** [`grafana_mcp_client.py`](file:///Users/satheesh/e2b_docker/backend/services/grafana_mcp_client.py)
- Uses Groq LLM to create dashboards
- Sends structured prompts with experiment data
- Parses LLM responses for dashboard URLs
- Falls back to mock URLs if MCP fails

**Updated:** [`main.py`](file:///Users/satheesh/e2b_docker/backend/main.py)
- Now uses `GrafanaMCPClient` instead of `GrafanaClient`
- Passes analysis summary to give LLM context
- LLM creates dashboards based on experiment results

### Benefits

✅ **Intelligent Dashboard Creation** - LLM understands the data and creates appropriate visualizations

✅ **Natural Language Interface** - Describe what you want, LLM figures out how to create it

✅ **Flexible** - Easy to modify dashboard requirements by changing the prompt

✅ **MCP Protocol** - Uses standard Model Context Protocol for Grafana interaction

✅ **Fallback** - Returns mock URLs if MCP server isn't available

### Configuration

Your `.env` already has everything needed:

```bash
# Groq (used for both analysis AND dashboard creation)
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant

# Grafana MCP Server
GRAFANA_MCP_URL=http://localhost:8000
```

### Testing

**1. Make sure your Grafana MCP server is running:**
```bash
# Check if it's up
curl http://localhost:8000/health
# or
lsof -i :8000
```

**2. Restart the backend:**
```bash
cd backend
python main.py
```

**3. Run an experiment:**
- Go to http://localhost:5173
- Select a chaos scenario
- Start experiment
- Watch the logs for LLM dashboard creation!

### What You'll See in Logs

```
2025-11-22 14:05:00 - INFO - Using LLM to create Grafana dashboard for experiment: exp_abc123
2025-11-22 14:05:00 - INFO - Calling Groq to create dashboard via MCP...
2025-11-22 14:05:02 - INFO - LLM response: {"dashboard_url": "http://localhost:8000/d/...", "success": true}
2025-11-22 14:05:02 - INFO - Dashboard created via LLM+MCP: http://localhost:8000/d/...
```

### Customizing Dashboard Creation

Edit the prompt in `grafana_mcp_client.py` to change what dashboards look like:

```python
def _build_mcp_prompt(self, ...):
    return f"""Create a Grafana dashboard...
    
    **Dashboard Requirements:**
    1. Title: "..."
    2. Panels needed:
       - Add your custom panel requirements here
       - Specify colors, thresholds, etc.
    """
```

### Troubleshooting

**If dashboards aren't created:**
1. Check Grafana MCP server is running on port 8000
2. Check Groq API key is valid
3. Look at backend logs for LLM responses
4. App will fall back to mock URLs automatically

**The app works perfectly even without Grafana MCP** - you'll just get mock URLs instead of real dashboards!

---

## 🎉 You Now Have LLM-Powered Dashboard Creation!

Your chaos experiments now automatically generate intelligent Grafana dashboards using AI! 🚀
