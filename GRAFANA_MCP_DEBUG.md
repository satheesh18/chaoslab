# 🔍 Grafana MCP Debugging Guide

## Issue
No logs appearing for Grafana MCP dashboard creation, and dashboard URLs return 404.

## What I Added

**Enhanced logging in `grafana_mcp_client.py`:**

- ✅ Detailed step-by-step logging
- ✅ Request/response body logging
- ✅ Separate exception handling for network vs other errors
- ✅ Full traceback on errors
- ✅ Emoji indicators for easy scanning (✅ ❌ ⚠️)

## To Debug

**1. Restart the backend:**
```bash
cd backend
python main.py
```

**2. Run a new experiment** at http://localhost:5173

**3. Check the logs** - you should now see detailed output like:

```
=== Starting Grafana MCP dashboard creation for exp_abc123 ===
MCP URL: http://localhost:8000
Building dashboard JSON...
Dashboard JSON built successfully (size: 12345 chars)
Sending MCP request to http://localhost:8000/
MCP request method: tools/call, tool: update_dashboard
MCP response status: 200
MCP response body: {...}
```

## Common Issues & Solutions

### Issue 1: No MCP logs at all
**Cause:** Exception being caught in main.py  
**Solution:** Check main.py exception handling around line 170-180

### Issue 2: "Network error calling MCP server"
**Cause:** Grafana MCP server not running or wrong URL  
**Solution:**
```bash
# Check if MCP server is running
curl http://localhost:8000/healthz
# Should return: ok

# Check what's on port 8000
lsof -i :8000
```

### Issue 3: "MCP request failed with status XXX"
**Cause:** MCP server returned error  
**Solution:** Check the response body in logs for error details

### Issue 4: Dashboard URL 404
**Possible causes:**
1. Dashboard not actually created in Grafana
2. Wrong Grafana URL (should be port 3000, not 8000)
3. Dashboard UID mismatch

**Check:**
```bash
# List dashboards in Grafana
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:3000/api/search?type=dash-db

# Check if dashboard exists
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:3000/api/dashboards/uid/chaoslab-exp_abc123
```

## MCP Server Requirements

Your Grafana MCP server needs:

1. **Running on port 8000**
   ```bash
   lsof -i :8000
   ```

2. **Accessible endpoint**
   ```bash
   curl http://localhost:8000/healthz
   ```

3. **Proper authentication** to Grafana
   - Service account token
   - Permissions: `dashboards:write`

4. **Grafana instance running** on port 3000
   ```bash
   curl http://localhost:3000/api/health
   ```

## Test MCP Manually

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
          "dashboard": {
            "title": "Test Dashboard",
            "uid": "test-123",
            "panels": []
          },
          "overwrite": true
        }
      }
    }
  }'
```

Expected response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "uid": "test-123",
    "url": "/d/test-123/test-dashboard"
  }
}
```

## Next Steps

1. **Run a new experiment** with the enhanced logging
2. **Share the logs** - look for lines starting with `===` or containing `MCP`
3. **Check MCP server logs** if available
4. **Verify Grafana connectivity** from the MCP server

The detailed logs will tell us exactly where it's failing! 🔍
