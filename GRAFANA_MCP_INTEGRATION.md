# 🎨 Grafana MCP Integration

## How It Works

ChaosLab now integrates with your **Grafana MCP server** using the **Model Context Protocol** to automatically create dashboards for chaos experiments!

### Architecture

```
┌──────────────────────────────────────────────────────┐
│  ChaosLab Backend (localhost:9000)                   │
│                                                       │
│  1. Run Experiment → Collect Metrics                 │
│  2. Groq Analyzes → Extract Insights                 │
│  3. MCP Protocol → Create Dashboard                  │
│     │                                                 │
│     │  JSON-RPC Request:                             │
│     │  {                                              │
│     │    "method": "tools/call",                      │
│     │    "params": {                                  │
│     │      "name": "update_dashboard",                │
│     │      "arguments": { dashboard JSON }            │
│     │    }                                            │
│     │  }                                              │
│     ▼                                                 │
│  ┌────────────────────────────────┐                  │
│  │  Grafana MCP Server            │                  │
│  │  localhost:8000                │                  │
│  │  - Receives MCP request        │                  │
│  │  - Calls update_dashboard tool │                  │
│  │  - Creates dashboard in Grafana│                  │
│  │  - Returns dashboard UID        │                  │
│  └────────────────────────────────┘                  │
└──────────────────────────────────────────────────────┘
```

### MCP Protocol

The integration uses the **Model Context Protocol** (JSON-RPC 2.0) to call the `update_dashboard` tool provided by your Grafana MCP server.

**Request Format:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "update_dashboard",
    "arguments": {
      "dashboard": {
        "dashboard": {
          "title": "Chaos Experiment: network_delay - exp_abc123",
          "uid": "chaoslab-exp_abc123",
          "panels": [ ... ]
        },
        "overwrite": true
      },
      "message": "Created by ChaosLab",
      "overwrite": true
    }
  }
}
```

### Dashboard Structure

Each dashboard includes:

1. **Summary Panel** - Markdown text with experiment details
2. **CPU Gauge** - Peak CPU usage with thresholds
3. **Memory Gauge** - Peak memory usage with thresholds  
4. **Error Count** - Stat panel with error count
5. **Recovery Time** - Stat panel showing recovery time

### Configuration

Your `.env` needs:

```bash
# Grafana MCP Server (running locally)
GRAFANA_MCP_URL=http://localhost:8000

# Groq (for log analysis only)
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant
```

### Testing

**1. Ensure Grafana MCP server is running:**
```bash
# Check if it's up
curl http://localhost:8000/healthz
# Should return: ok

# Or check with lsof
lsof -i :8000
```

**2. Restart ChaosLab backend:**
```bash
cd backend
python main.py
```

**3. Run an experiment:**
- Go to http://localhost:5173
- Select a chaos scenario
- Start experiment
- Check logs for MCP dashboard creation!

### What You'll See in Logs

```
2025-11-22 14:15:00 - INFO - Creating Grafana dashboard via MCP for experiment: exp_abc123
2025-11-22 14:15:00 - INFO - Calling MCP update_dashboard tool at http://localhost:8000
2025-11-22 14:15:01 - INFO - Dashboard created via MCP: http://localhost:3000/d/chaoslab-exp_abc123
```

### MCP Tools Used

From your Grafana MCP server, we use:

- **`update_dashboard`** - Creates or updates a dashboard
  - Takes full dashboard JSON
  - Returns dashboard UID
  - Requires `dashboards:write` permission

### Troubleshooting

**If dashboards aren't created:**

1. **Check MCP server is running:**
   ```bash
   curl http://localhost:8000/healthz
   ```

2. **Check MCP server logs** for errors

3. **Verify permissions** - Service account needs `dashboards:write`

4. **Test MCP endpoint manually:**
   ```bash
   curl -X POST http://localhost:8000/ \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": 1,
       "method": "tools/call",
       "params": {
         "name": "update_dashboard",
         "arguments": {
           "dashboard": {
             "dashboard": {"title": "Test"},
             "overwrite": true
           }
         }
       }
     }'
   ```

**Fallback Behavior:**

If MCP call fails, the app automatically falls back to mock URLs:
- `http://localhost:3000/d/chaoslab-{experiment_id}`
- Results still display perfectly
- You just won't see the actual Grafana visualization

### Benefits

✅ **Direct MCP Integration** - Uses standard Model Context Protocol

✅ **Automatic Dashboard Creation** - No manual setup needed

✅ **Rich Visualizations** - Gauges, stats, and markdown panels

✅ **Experiment Tracking** - Each experiment gets its own dashboard

✅ **Fallback Support** - Works even if Grafana MCP is unavailable

---

## 🎉 Your Chaos Experiments Now Auto-Create Grafana Dashboards!

Using the Model Context Protocol, every experiment automatically generates a beautiful Grafana dashboard! 🚀
