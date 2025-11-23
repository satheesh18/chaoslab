# Timeline Metrics Implementation

## Overview
Implemented real-time time-series metrics collection for chaos experiments, replacing fake/estimated data with actual measurements.

## Changes Made

### 1. Backend - E2B Manager (`backend/services/e2b_manager.py`)
- **Added `_create_metrics_monitor_script()`**: Creates a bash script that samples metrics every 5 seconds during the experiment
  - Monitors CPU usage (converting from idle % to usage %)
  - Monitors memory usage percentage
  - Tracks cumulative error count from Flask logs
  - Saves data to `/tmp/metrics_timeseries.csv` in the sandbox

- **Added `_collect_timeseries_metrics()`**: Parses the CSV and returns structured timeline data
  - Reads the CSV file from the sandbox
  - Calculates peak CPU, peak memory, and total errors
  - Attempts to detect recovery time (when metrics return to normal)
  - Returns full timeline array with data points

- **Updated `run_chaos_script()`**: Now runs metrics monitoring in parallel with chaos script
  - Starts background monitoring script
  - Runs chaos script
  - Collects time-series data after completion

### 2. Backend - Groq Analyzer (`backend/services/groq_analyzer.py`)
- **Updated `_create_analysis_prompt()`**: Now includes actual timeline data in the prompt
  - Shows peak metrics upfront
  - Includes sample timeline data points
  - Instructs Groq to use real data, not estimates

- **Updated `_fallback_analysis()`**: Uses actual collected metrics instead of hardcoded values
  - Takes metrics from the collected timeline
  - Calculates severity based on real data
  - Returns actual timeline array

- **Updated system prompt**: Added instruction to return timeline data in JSON response

### 3. Backend - Models (`backend/models.py`)
- **Added `TimelineDataPoint` model**: Defines structure for time-series data
  ```python
  time_offset: int  # Seconds from start
  cpu: float        # CPU usage %
  memory: float     # Memory usage %
  error_count: int  # Cumulative errors
  ```

- **Updated `ResultsResponse` model**: Added optional `timeline` field

### 4. Backend - Main API (`backend/main.py`)
- **Updated `/api/experiment/{id}/results` endpoint**: Now includes timeline in response
  - Passes `analysis.get("timeline", [])` to ResultsResponse

### 5. Frontend - API Client (`frontend/src/api/client.ts`)
- **Added `TimelineDataPoint` interface**: TypeScript type definition
- **Updated `ResultsResponse` interface**: Added optional `timeline` field

### 6. Frontend - Timeline Chart Component (`frontend/src/components/TimelineChart.tsx`)
- **Created new component**: Renders SVG chart with CPU, memory, and error data
  - Dual-line chart (CPU in blue, Memory in green)
  - Error markers as red dots with counts
  - Grid lines and axis labels
  - Responsive legend
  - Summary stats (data points, duration, sampling rate)

### 7. Frontend - Results View (`frontend/src/components/ResultsView.tsx`)
- **Integrated TimelineChart**: Displays timeline if data is available
- **Fixed recovery time display**: Shows "N/A" when null instead of crashing

## Key Improvements

### Before:
- ❌ Single snapshot of CPU/memory at the end
- ❌ Fake/estimated timeline data in Groq fallback
- ❌ Error count mismatch (raw vs analyzed)
- ❌ Hardcoded recovery time (always 8.0s)

### After:
- ✅ Time-series data collected every 5 seconds
- ✅ Real metrics used everywhere
- ✅ Accurate error counting from logs
- ✅ Calculated recovery time (or null if not detected)
- ✅ Visual timeline chart in UI
- ✅ Groq receives and returns actual timeline data

## Data Flow

```
Experiment Start
    ↓
Create Sandbox
    ↓
Deploy Flask App
    ↓
Start Metrics Monitor (background) ──→ Sample every 5s ──→ Write to CSV
    ↓
Run Chaos Script (60s)
    ↓
Wait for completion
    ↓
Read CSV from sandbox
    ↓
Parse into timeline array
    ↓
Calculate peaks & recovery time
    ↓
Send to Groq for analysis
    ↓
Groq returns analysis with timeline
    ↓
Store in experiment results
    ↓
Return to frontend
    ↓
Display timeline chart
```

## Example Timeline Data

```json
{
  "timeline": [
    {"time_offset": 0, "cpu": 5.2, "memory": 22.1, "error_count": 0},
    {"time_offset": 5, "cpu": 8.4, "memory": 23.5, "error_count": 0},
    {"time_offset": 10, "cpu": 12.1, "memory": 24.8, "error_count": 1},
    {"time_offset": 15, "cpu": 45.3, "memory": 35.2, "error_count": 2},
    ...
  ],
  "cpu_peak": 45.3,
  "memory_peak": 35.2,
  "error_count": 4,
  "recovery_time_seconds": 25
}
```

## Testing

To test the new implementation:

1. Start the backend: `cd backend && python main.py`
2. Start the frontend: `cd frontend && npm run dev`
3. Run an experiment with any scenario
4. Check the results page for the timeline chart
5. Verify metrics match the timeline data
6. Check `backend/experiment_results/exp_*.json` for saved timeline data

## Notes

- Metrics sampling interval: 5 seconds (configurable in `_create_metrics_monitor_script`)
- Timeline data is saved to experiment result files for later analysis
- Recovery time detection: looks for CPU < 30% and Memory < 50% after initial spike
- Chart auto-scales based on data range
- Handles edge cases: no timeline data, null recovery time, zero errors
