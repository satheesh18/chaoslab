# Grafana Timeline Charts Implementation

## Overview
Moved timeline visualization from frontend to Grafana dashboards, where it properly belongs. Now Grafana displays comprehensive time-series charts using the collected metrics data.

## Changes Made

### 1. Backend - Grafana MCP Client (`backend/services/grafana_mcp_client.py`)

#### Updated Dashboard Builder
- **Enhanced `_build_dashboard_json()`**: Creates proper time-series panels with real timeline data
  - Generates two CSV datasets:
    - `csv_resources`: CPU and Memory over time
    - `csv_errors`: Error count over time
  - Uses absolute timestamps for proper time-series visualization
  - Calculates time range from actual timeline data

#### New Dashboard Layout
1. **Summary Panel** (top)
   - Markdown text with experiment details
   - Shows scenario, summary, peak metrics, and data point count

2. **CPU & Memory Time Series** (main chart, left)
   - Dual-line graph showing CPU (blue) and Memory (green)
   - Smooth interpolation with gradient fill
   - Auto-scaled 0-100%
   - Interactive tooltip with both metrics

3. **Error Count Time Series** (right)
   - Bar chart showing cumulative errors over time
   - Color-coded by severity (green/yellow/red)
   - Step-after interpolation for accuracy

4. **Metric Gauges** (bottom row)
   - Peak CPU gauge with thresholds
   - Peak Memory gauge with thresholds
   - Total Errors stat panel
   - Recovery Time stat panel

### 2. Frontend - Results View (`frontend/src/components/ResultsView.tsx`)
- **Removed TimelineChart import**: No longer needed in frontend
- **Removed inline timeline chart**: Charts now only in Grafana
- **Kept Grafana iframe**: Embedded dashboard shows all visualizations

### 3. Frontend - TimelineChart Component
- **Component still exists** but unused (can be deleted if desired)
- All visualization now happens in Grafana

## Dashboard Features

### Time-Series Charts
- **Real data**: Uses actual collected metrics from E2B sandbox
- **Proper timestamps**: Absolute time values for accurate timeline
- **Multiple series**: CPU, Memory, and Errors on separate optimized charts
- **Interactive**: Hover tooltips, zoom, pan capabilities
- **Auto-scaling**: Charts adjust to data ranges automatically

### Visual Design
```
┌─────────────────────────────────────────────────────────┐
│  Experiment Summary                                      │
│  Scenario details, metrics, data point count            │
├──────────────────────────────────┬──────────────────────┤
│  CPU & Memory Time Series        │  Error Count         │
│  ─────────────────────────       │  ▮▮▮▮▮▮▮▮▮          │
│  Blue: CPU    Green: Memory      │  Bar chart           │
│  Smooth lines, gradient fill     │  Cumulative errors   │
├────────┬────────┬────────┬────────┤                      │
│ CPU %  │ Mem %  │ Errors │Recovery│                      │
│ Gauge  │ Gauge  │ Stat   │ Stat   │                      │
└────────┴────────┴────────┴────────┘
```

## Data Flow

```
Timeline collected in E2B
    ↓
Passed to Grafana MCP Client
    ↓
Convert to CSV format:
  - time,cpu,memory
  - time,errors
    ↓
Create Grafana panels:
  - Time-series for CPU/Memory
  - Time-series for Errors
  - Gauges for peaks
  - Stats for totals
    ↓
Send to Grafana via MCP
    ↓
Dashboard created
    ↓
Frontend embeds dashboard iframe
    ↓
User sees full time-series visualization
```

## Example CSV Data

### Resource Metrics (CPU & Memory)
```csv
time,cpu,memory
1700000000000,5.2,22.1
1700000005000,8.4,23.5
1700000010000,12.1,24.8
1700000015000,45.3,35.2
...
```

### Error Metrics
```csv
time,errors
1700000000000,0
1700000005000,0
1700000010000,1
1700000015000,2
...
```

## Benefits

### Before (Frontend Timeline):
- ❌ Simple SVG chart in React
- ❌ Limited interactivity
- ❌ Separate from other Grafana metrics
- ❌ Not shareable
- ❌ No Grafana features

### After (Grafana Timeline):
- ✅ Professional time-series visualization
- ✅ Full Grafana interactivity (zoom, pan, hover)
- ✅ Integrated with other dashboard panels
- ✅ Shareable Grafana dashboard URL
- ✅ Consistent with monitoring best practices
- ✅ Better for analysis and reporting
- ✅ Leverages Grafana's TestData datasource

## Testing

1. Start backend: `cd backend && python main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Run an experiment
4. Click the Grafana dashboard link in results
5. Verify time-series charts show:
   - CPU and Memory lines over time
   - Error bars when errors occurred
   - Correct time range and data points
   - Interactive tooltips and legends

## Notes

- Uses Grafana's TestData datasource with CSV metric values
- Timeline data must have `time_offset`, `cpu`, `memory`, and `error_count` fields
- Timestamps are converted to absolute milliseconds for Grafana
- Charts auto-refresh is disabled since data is static (historical)
- Dashboard UIDs are unique per experiment: `chaoslab-{experiment_id}`
- Time range is automatically set based on experiment duration

## Cleanup (Optional)

The frontend TimelineChart component at `frontend/src/components/TimelineChart.tsx` is no longer used and can be deleted:

```bash
rm frontend/src/components/TimelineChart.tsx
```

Also remove the timeline type from `frontend/src/api/client.ts` if you want to clean up unused types (though keeping it doesn't hurt).
