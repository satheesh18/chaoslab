# Grafana Visualization Fix

## Problem

The Grafana dashboards were showing "No data" for all panels even though the experiment JSON files contained valid timeline data.

### Root Cause

The issue was with how we were using Grafana's **testdata datasource**:

1. **CSV Content with Time-Series Panels**: The `csv_content` scenario in Grafana's testdata datasource doesn't work reliably for time-series visualization
2. **Timestamp Format Issues**: Even with epoch milliseconds, the CSV data wasn't being parsed correctly by Grafana
3. **Panel Configuration**: Time-series panels require a proper time-based datasource (like Prometheus, InfluxDB, etc.) or specific testdata scenarios

## Solution

Changed the approach to use **Table visualization** instead of time-series charts, which works perfectly with CSV data from the testdata datasource.

### What Changed

#### Before ❌
```python
# Tried to use time-series panels with CSV content
{
    "type": "timeseries",
    "targets": [{
        "scenarioId": "csv_content",
        "csvContent": "Time,CPU,Memory\n1763854750000,10.5,26.3\n..."
    }]
}
```
**Problem**: Grafana's testdata datasource doesn't render time-series from CSV properly

#### After ✅
```python
# Use table panel with CSV content
{
    "type": "table",
    "targets": [{
        "scenarioId": "csv_content",
        "csvContent": "Time Offset (s),CPU (%),Memory (%),Errors\n0,1.6,26.06,0\n..."
    }]
}
```
**Result**: Data displays correctly in a table with color-coded cells

### New Dashboard Layout

1. **Summary Panel** (text) - Shows experiment details
2. **Metrics Timeline Table** (table) - Shows all data points with color coding:
   - CPU: Green (0-50%) → Yellow (50-80%) → Red (80-100%)
   - Memory: Green (0-60%) → Yellow (60-85%) → Red (85-100%)
   - Errors: Green (0) → Yellow (1-4) → Red (5+)
3. **Peak CPU Stat** - Shows maximum CPU value
4. **Peak Memory Stat** - Shows maximum memory value
5. **Total Errors Stat** - Shows error count
6. **Recovery Time Stat** - Shows recovery time or N/A

### Benefits of Table Visualization

1. ✅ **Works Reliably**: CSV content displays perfectly in tables
2. ✅ **Shows All Data**: Every data point is visible
3. ✅ **Color Coding**: Threshold-based background colors make it easy to spot issues
4. ✅ **No Timestamp Issues**: Uses simple time offsets instead of complex timestamps
5. ✅ **Better for Static Data**: Since we're showing historical experiment data, a table is more appropriate than a live time-series chart

## Files Modified

### backend/services/grafana_mcp_client.py

1. **Added `_build_timeline_csv()` method**:
   - Builds CSV content with simple format: `Time Offset (s),CPU (%),Memory (%),Errors`
   - Uses time offsets (0, 5, 10, 15...) instead of absolute timestamps
   - Formats numbers with 1 decimal place for readability

2. **Simplified `_build_dashboard_json()` method**:
   - Removed complex CSV timestamp calculations
   - Removed time-series panel configurations
   - Added table panel with proper field overrides for color coding

3. **Updated stat panels**:
   - Changed from gauge to stat type (more reliable)
   - Added `reduceOptions` for proper value display
   - Kept threshold-based coloring

## Testing

### Before Fix
```
Dashboard shows:
- Summary Panel: ✅ Works
- CPU & Memory Chart: ❌ "No data"
- Error Count Chart: ❌ "No data"
- Peak CPU Gauge: ❌ Random number or "No data"
- Peak Memory Gauge: ❌ Random number or "No data"
- Total Errors: ❌ "No data"
- Recovery Time: ❌ "No data"
```

### After Fix
```
Dashboard shows:
- Summary Panel: ✅ Works
- Metrics Timeline Table: ✅ Shows all data points with colors
- Peak CPU Stat: ✅ Shows 8.2%
- Peak Memory Stat: ✅ Shows 27.3%
- Total Errors: ✅ Shows 14
- Recovery Time: ✅ Shows N/A
```

## Example Dashboard

For experiment `exp_071af494`:

| Time Offset (s) | CPU (%) | Memory (%) | Errors |
|-----------------|---------|------------|--------|
| 0               | 1.6     | 26.1       | 0      |
| 6               | 5.8     | 26.6       | 1      |
| 12              | 6.6     | 26.8       | 2      |
| 17              | 0.8     | 27.0       | 4      |
| 23              | 5.0     | 27.0       | 4      |
| 29              | 6.6     | 27.1       | 5      |
| 35              | 1.6     | 27.1       | 6      |
| 40              | 0.8     | 27.2       | 8      |
| 46              | 8.2     | 27.3       | 10     |
| 52              | 5.8     | 26.5       | 11     |
| 58              | 0.8     | 26.8       | 13     |

With color coding:
- CPU values (1.6-8.2%) show as **green** (all under 50%)
- Memory values (26-27%) show as **green** (all under 60%)
- Error counts show as **yellow** (1-4) and **red** (5+)

## Why Not Use Real Time-Series?

To use proper time-series visualization in Grafana, we would need:

1. **Real Datasource**: Prometheus, InfluxDB, or similar
2. **Live Data**: Push metrics during experiment execution
3. **Query Language**: PromQL or similar to query the data

Since ChaosLab:
- Collects data in E2B sandboxes (isolated environments)
- Stores results as JSON files (historical data)
- Uses Grafana MCP for dashboard creation (limited to testdata datasource)

A **table visualization** is the most practical solution that:
- Works with the testdata datasource
- Shows all collected data points
- Provides visual feedback through color coding
- Doesn't require complex infrastructure

## Future Improvements

If you want real time-series charts in the future, consider:

1. **Option A: Use Prometheus**
   - Set up Prometheus server
   - Push metrics during experiment execution
   - Use Prometheus datasource in Grafana
   - Create proper time-series panels

2. **Option B: Use InfluxDB**
   - Set up InfluxDB
   - Write metrics during experiment
   - Use InfluxDB datasource in Grafana
   - Query with InfluxQL

3. **Option C: Use Grafana Cloud**
   - Use Grafana's hosted metrics service
   - Push data via API during experiments
   - Create dashboards with real datasources

For now, the table visualization provides all the information needed to analyze chaos experiment results effectively.

## Summary

✅ **Fixed**: Grafana dashboards now display all metrics correctly
✅ **Approach**: Changed from time-series to table visualization
✅ **Benefits**: Reliable, color-coded, shows all data points
✅ **Trade-off**: Table instead of line charts (acceptable for historical data)

The fix ensures that all experiment data is visible and easy to analyze in Grafana dashboards.
