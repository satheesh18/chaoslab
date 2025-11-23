# Testing the Metrics Fixes

## Quick Test Guide

### Step 1: Start the Backend
```bash
cd backend
source venv/bin/activate  # if using venv
python main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:9000
```

### Step 2: Start the Frontend
```bash
cd frontend
npm run dev
```

Expected output:
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
```

### Step 3: Run an Experiment

1. Open http://localhost:5173
2. Select **Network Delay** scenario
3. Set duration to **60 seconds**
4. Set intensity to **Medium**
5. Click **Start Chaos Experiment**

### Step 4: Monitor Progress

Watch the backend logs for:
```
INFO - Creating sandbox for exp_XXXXXXXX
INFO - Deploying test app for exp_XXXXXXXX
INFO - Running chaos script for exp_XXXXXXXX
INFO - Analyzing results with Groq for exp_XXXXXXXX
INFO - Creating Grafana dashboard for exp_XXXXXXXX
INFO - Experiment exp_XXXXXXXX completed successfully
```

### Step 5: Verify Results

#### A. Check Stored Data
```bash
cd backend
python test_metrics_fix.py
```

Look for the new experiment:
```
🔍 Analyzing exp_XXXXXXXX...
  ✅ Timeline: 12 data points
  ✅ CPU: peak=XX.X%, avg=XX.X%    # Should NOT be 0%
  ✅ Memory: peak=XX.X%, avg=XX.X%
  ✅ Errors: X
  ✅ Grafana URL: http://...
```

#### B. Check Grafana Dashboard

1. Copy the Grafana URL from the results
2. Open it in your browser
3. Verify:
   - ✅ **Summary panel** shows experiment details
   - ✅ **CPU & Memory chart** displays lines (not empty)
   - ✅ **Error count chart** shows bars
   - ✅ **Peak CPU gauge** shows a number (not random)
   - ✅ **Peak Memory gauge** shows a number
   - ✅ **Total Errors stat** shows correct count
   - ✅ **Recovery Time stat** shows time or N/A

#### C. Check Raw JSON
```bash
cat backend/experiment_results/exp_XXXXXXXX.json | jq '.raw_metrics.timeline[0:3]'
```

Expected output:
```json
[
  {
    "time_offset": 0,
    "cpu": 5.2,        # Should NOT be 0.0
    "memory": 26.1,
    "error_count": 0
  },
  {
    "time_offset": 5,
    "cpu": 15.8,       # Should vary
    "memory": 26.3,
    "error_count": 0
  },
  ...
]
```

### Step 6: Compare with Old Experiments

Run the diagnostic tool to see the difference:
```bash
cd backend
python test_metrics_fix.py
```

You should see:
- **Old experiments**: CPU always 0% or missing timeline
- **New experiment**: Realistic CPU values and complete timeline

---

## What to Look For

### ✅ Good Signs
- CPU values vary between 5-100%
- Timeline has 12+ data points
- Grafana charts display properly
- Gauge panels show actual values (not random)
- Memory usage is realistic (20-80%)

### ❌ Bad Signs (Indicates Fix Didn't Work)
- CPU is always 0.0%
- Timeline is empty or missing
- Grafana charts are blank
- Gauge panels show random numbers
- Errors in backend logs

---

## Troubleshooting

### If CPU is still 0%
1. Check E2B sandbox logs in backend output
2. Verify the monitoring script is running: look for `/tmp/metrics_timeseries.csv` in logs
3. Try a different scenario (memory_pressure generates more load)

### If Grafana charts are empty
1. Check the CSV data in backend logs (search for "CSV Resources sample")
2. Verify timestamps are in epoch milliseconds format
3. Check Grafana MCP server is running on port 8000

### If you see errors
1. Check E2B API key is valid
2. Verify Groq API key is set
3. Check backend logs for detailed error messages
4. Ensure all dependencies are installed

---

## Expected Timeline

- **Sandbox creation**: 10-20 seconds
- **App deployment**: 5-10 seconds
- **Chaos execution**: 60 seconds (configurable)
- **Metrics collection**: 3 seconds
- **Groq analysis**: 2-5 seconds
- **Grafana dashboard**: 1-3 seconds
- **Total**: ~80-100 seconds for a 60-second experiment

---

## Success Criteria

Your experiment is successful if:

1. ✅ Backend completes without errors
2. ✅ Timeline has data points (not empty)
3. ✅ CPU values are realistic (not 0%)
4. ✅ Grafana dashboard displays all charts
5. ✅ Gauge panels show correct values
6. ✅ Results are saved to JSON file

If all criteria are met, the fixes are working correctly! 🎉
