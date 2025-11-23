# Final Grafana Visualization Fix

## What Was Fixed

The Grafana dashboards were showing "No data" even though experiment data was being collected correctly. The issue was with the **testdata datasource UID**.

### Root Cause

Grafana's testdata datasource has a unique UID that varies between installations. We were using a hardcoded UID (`PD8C576611E62080A`) that didn't exist in your Grafana instance.

### Solution

The code now **automatically detects** the testdata datasource UID from your Grafana instance:

1. On initialization, it queries Grafana's API: `GET /api/datasources`
2. Finds the testdata datasource and extracts its UID
3. Uses that UID in all dashboard panels
4. Falls back to a default UID if the API call fails

## Changes Made

### backend/services/grafana_mcp_client.py

1. **Added `_get_testdata_datasource()` method**:
   - Queries Grafana API to find testdata datasource
   - Stores the UID in `self.testdata_uid`
   - Falls back to default if API fails

2. **Updated all panel datasource references**:
   - Changed from hardcoded UID to dynamic `self.testdata_uid`
   - Uses conditional expression for fallback

3. **Improved dashboard creation**:
   - Better error handling
   - Fallback to direct Grafana API if MCP fails
   - More detailed logging

## How It Works Now

```python
# On initialization
self._get_testdata_datasource()  # Finds UID from Grafana

# In dashboard panels
"datasource": {
    "type": "testdata", 
    "uid": self.testdata_uid  # Uses detected UID
} if self.testdata_uid else {"type": "testdata"}
```

## Testing

### Step 1: Restart Backend
```bash
# Stop the backend (Ctrl+C)
# Start it again
cd backend
python main.py
```

You should see in the logs:
```
INFO - Found testdata datasource UID: XXXXX
```

### Step 2: Run New Experiment
1. Open http://localhost:5173
2. Run a new chaos experiment
3. Wait for completion
4. Click on the Grafana dashboard link

### Step 3: Verify Dashboard
The dashboard should now show:
- ✅ **Metrics Timeline table** with all data points (color-coded)
- ✅ **Peak CPU stat** showing actual value (e.g., 56.7%)
- ✅ **Peak Memory stat** showing actual value (e.g., 28.5%)
- ✅ **Total Errors stat** showing count (e.g., 15)
- ✅ **Recovery Time stat** showing time or N/A

## Expected Output

### Metrics Timeline Table
| Time (s) | CPU (%) | Memory (%) | Errors |
|----------|---------|------------|--------|
| 0        | 1.7     | 26.1       | 0      |
| 6        | 8.1     | 26.8       | 1      |
| 11       | 56.7    | 28.5       | 3      |
| ...      | ...     | ...        | ...    |

With color coding:
- Green: Normal values
- Yellow: Warning threshold
- Red: Critical threshold

### Stat Panels
- Peak CPU: **56.7%** (colored based on threshold)
- Peak Memory: **28.5%** (colored based on threshold)
- Total Errors: **15** (colored based on threshold)
- Recovery Time: **N/A** or time in seconds

## Troubleshooting

### If Still Showing "No data"

1. **Check Grafana is running**:
   ```bash
   curl http://localhost:3000/api/health
   ```

2. **Check testdata datasource exists**:
   ```bash
   curl http://localhost:3000/api/datasources | jq '.[] | select(.type=="testdata")'
   ```

3. **Check backend logs** for:
   ```
   Found testdata datasource UID: XXXXX
   ```

4. **Manually verify datasource**:
   - Open Grafana UI: http://localhost:3000
   - Go to Configuration → Data Sources
   - Verify "TestData DB" exists

### If Datasource Not Found

If Grafana doesn't have a testdata datasource, you need to add it:

1. Go to Configuration → Data Sources
2. Click "Add data source"
3. Select "TestData DB"
4. Click "Save & Test"

## Alternative: Use Grafana MCP Properly

If you want to use the Grafana MCP server (running on port 8000) properly, you need to:

1. Ensure MCP server has proper Grafana credentials
2. Use MCP tools like `list_datasources`, `update_dashboard`
3. Follow the MCP protocol correctly

The current implementation tries MCP first, then falls back to direct Grafana API.

## Summary

✅ **Fixed**: Datasource UID is now detected automatically
✅ **Improved**: Better error handling and fallbacks
✅ **Result**: Grafana dashboards should now display all metrics correctly

Run a new experiment to test the fix!
