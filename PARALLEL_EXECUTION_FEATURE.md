# Parallel Execution Feature

## Overview

Added support for running chaos experiments across multiple E2B sandboxes in parallel and averaging the results. This provides more reliable metrics by reducing variance from single-run experiments.

## Features

### Frontend
- **New Slider**: "Parallel Instances" (1-5 instances)
- **Visual Feedback**: Shows "Nx" and info message when > 1 instance
- **Same UI Flow**: No changes to existing workflow

### Backend
- **Parallel Execution**: Uses ThreadPoolExecutor to run experiments concurrently
- **Metric Averaging**: Averages CPU, Memory, and Error counts across all instances
- **Timeline Alignment**: Aligns and averages timeline data point-by-point
- **Graceful Degradation**: If some instances fail, uses successful ones

### Data Format
- **No Breaking Changes**: Output format remains identical
- **Additional Field**: `num_instances` added to metadata
- **Grafana Compatible**: All existing visualizations work unchanged

## How It Works

### Single Instance (num_instances = 1)
```
User Request → E2B Sandbox → Run Experiment → Return Metrics
```

### Multiple Instances (num_instances > 1)
```
User Request → ThreadPoolExecutor
                ├─ E2B Sandbox 1 → Run Experiment → Metrics 1
                ├─ E2B Sandbox 2 → Run Experiment → Metrics 2
                ├─ E2B Sandbox 3 → Run Experiment → Metrics 3
                └─ ...
                ↓
            Average Metrics → Return Averaged Results
```

## Averaging Logic

### Timeline Data
For each time offset:
- **CPU**: Average of all instance CPU values at that time
- **Memory**: Average of all instance memory values
- **Errors**: Average (rounded) of all instance error counts

### Peak Values
- **CPU Peak**: Average of peak CPU across all instances
- **Memory Peak**: Average of peak memory across all instances
- **Total Errors**: Average of total errors across all instances

### Example
```
Instance 1: CPU at 10s = 45.2%
Instance 2: CPU at 10s = 52.8%
Instance 3: CPU at 10s = 48.1%
→ Averaged: CPU at 10s = 48.7%
```

## Configuration

### Frontend (ExperimentForm.tsx)
```typescript
const [numInstances, setNumInstances] = useState(1);

<input
  type="range"
  min="1"
  max="5"
  step="1"
  value={numInstances}
  onChange={(e) => setNumInstances(Number(e.target.value))}
/>
```

### Backend (models.py)
```python
class ExperimentConfig(BaseModel):
    duration: int = Field(default=60, ge=10, le=300)
    intensity: str = Field(default="medium")
    num_instances: int = Field(default=1, ge=1, le=5)  # NEW
```

### E2B Manager (e2b_manager.py)
```python
def run_parallel_experiments(self, scenario, config, num_instances):
    # Create multiple E2B managers
    # Run experiments in parallel using ThreadPoolExecutor
    # Average the results
    return averaged_metrics
```

## Benefits

1. **More Reliable Metrics**: Reduces variance from single runs
2. **Better Insights**: Averaged data shows typical behavior
3. **Stress Testing**: Can test with higher load (multiple instances)
4. **No Breaking Changes**: Existing functionality unchanged
5. **Graceful Degradation**: Works even if some instances fail

## Limitations

1. **Cost**: Multiple E2B sandboxes = higher API usage
2. **Time**: Parallel execution still takes same duration (not faster)
3. **Max Instances**: Limited to 5 to prevent excessive resource usage
4. **Recovery Time**: Not averaged (doesn't make sense to average)

## Usage

### Via UI
1. Open ChaosLab frontend
2. Configure experiment as usual
3. Adjust "Parallel Instances" slider (1-5)
4. Click "Start Chaos Experiment"
5. Wait for completion
6. View averaged results in Grafana

### Via API
```bash
curl -X POST http://localhost:9000/api/experiment/start \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "network_delay",
    "config": {
      "duration": 60,
      "intensity": "medium",
      "num_instances": 3
    }
  }'
```

## Example Output

### Single Instance
```json
{
  "cpu_peak": 45.2,
  "memory_peak": 28.5,
  "error_count": 7,
  "num_instances": 1
}
```

### Multiple Instances (3x)
```json
{
  "cpu_peak": 48.7,  // Average of 45.2, 52.8, 48.1
  "memory_peak": 29.1,  // Average of 28.5, 30.2, 28.6
  "error_count": 6,  // Average of 7, 5, 6
  "num_instances": 3
}
```

## Grafana Dashboard

The dashboard automatically shows:
- **Instances**: "3 (averaged)" in summary panel
- **Charts**: Display averaged timeline data
- **Stats**: Show averaged peak values

No changes needed to existing dashboards!

## Testing

### Test Single Instance
```bash
# Should work exactly as before
num_instances: 1
```

### Test Multiple Instances
```bash
# Should create 3 sandboxes and average results
num_instances: 3
```

### Test Failure Handling
```bash
# If 1 out of 3 fails, should still return averaged results from 2
```

## Performance

### Single Instance
- Time: ~80-100 seconds (for 60s experiment)
- E2B API Calls: 1 sandbox

### Multiple Instances (3x)
- Time: ~80-100 seconds (parallel, not sequential!)
- E2B API Calls: 3 sandboxes
- CPU Usage: Higher (3 threads)

## Future Enhancements

1. **Progress Tracking**: Show individual instance progress
2. **Instance Comparison**: View metrics from each instance separately
3. **Outlier Detection**: Identify and flag anomalous instances
4. **Adaptive Instances**: Auto-determine optimal number based on variance
5. **Cost Estimation**: Show estimated E2B cost before running

## Summary

✅ **Added**: Parallel execution with 1-5 instances
✅ **Averaging**: Automatic metric averaging
✅ **No Breaking Changes**: Existing functionality preserved
✅ **UI Updated**: New slider in experiment form
✅ **Backend Updated**: Parallel execution with ThreadPoolExecutor
✅ **Grafana Compatible**: All visualizations work unchanged

Run experiments with multiple instances for more reliable chaos engineering insights!
