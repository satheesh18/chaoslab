# 📁 Experiment Results Storage

## Where Results Are Saved

Every experiment now saves its complete results to a JSON file in:

```
backend/experiment_results/{experiment_id}.json
```

## What's Included

Each JSON file contains:
- **experiment_id** - Unique identifier
- **scenario** - Which chaos scenario was run
- **config** - Duration, intensity settings
- **status** - Experiment status
- **created_at** - Timestamp
- **raw_metrics** - CPU, memory, logs from E2B sandbox
- **analysis** - Complete Groq AI analysis including:
  - Summary
  - Extracted metrics
  - Severity assessment
  - Recommendations
- **grafana_url** - Dashboard URL (mock or real)

## Example File Structure

```json
{
  "experiment_id": "exp_201bd5bc",
  "scenario": "network_delay",
  "config": {
    "duration": 60,
    "intensity": "medium"
  },
  "status": "completed",
  "created_at": "2025-11-22T13:53:21.044000",
  "raw_metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 62.8,
    "logs": "...",
    "error_count": 3
  },
  "analysis": {
    "summary": "Application handled network delay gracefully...",
    "metrics": {
      "cpu_peak": 45.2,
      "memory_peak": 62.8,
      "error_count": 3,
      "recovery_time_seconds": 8.5
    },
    "severity": "medium",
    "recommendations": [
      "Implement exponential backoff",
      "Add circuit breaker pattern"
    ]
  },
  "grafana_url": "http://localhost:8000/d/chaoslab-exp_201bd5bc/..."
}
```

## How to View Results

### Option 1: Check the Files
```bash
cd backend/experiment_results
ls -la
cat exp_*.json | jq '.'  # Pretty print with jq
```

### Option 2: View in VS Code
```bash
code backend/experiment_results/
```

### Option 3: Python Script
```python
import json
from pathlib import Path

results_dir = Path("backend/experiment_results")
for result_file in results_dir.glob("*.json"):
    with open(result_file) as f:
        data = json.load(f)
        print(f"\n{'='*50}")
        print(f"Experiment: {data['experiment_id']}")
        print(f"Scenario: {data['scenario']}")
        print(f"Summary: {data['analysis']['summary']}")
        print(f"Recommendations:")
        for rec in data['analysis']['recommendations']:
            print(f"  - {rec}")
```

## Restart Backend

```bash
# Stop with Ctrl+C, then:
cd backend
python main.py
```

## Run a New Experiment

After restarting, run a new experiment and you'll see:

```
2025-11-22 13:55:00,441 - main - INFO - Results saved to experiment_results/exp_201bd5bc.json
```

Then check:
```bash
cat backend/experiment_results/exp_201bd5bc.json
```

## Benefits

- ✅ **Persistent storage** - Results survive backend restarts
- ✅ **Easy verification** - Review AI analysis quality
- ✅ **Debugging** - See raw metrics and logs
- ✅ **Demo preparation** - Have example results ready
- ✅ **Comparison** - Compare different chaos scenarios

---

**The files are automatically created in `backend/experiment_results/` after each experiment completes!**
