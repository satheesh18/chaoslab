# Grafana Datasource Fix - Action Required

## Issue

The Grafana dashboards show "No data" because we're using a hardcoded testdata datasource UID that doesn't match your Grafana instance.

## Solution

You need to find the correct testdata datasource UID from your Grafana instance and update the code.

### Step 1: Get the Testdata Datasource UID

**Option A: Via Grafana UI**
1. Open Grafana: http://localhost:3000
2. Go to **Configuration** → **Data Sources**
3. Click on **TestData DB** (or similar)
4. Look at the URL - it will be like: `/datasources/edit/PD8C576611E62080A`
5. Copy the UID (e.g., `PD8C576611E62080A`)

**Option B: Via API**
```bash
curl http://localhost:3000/api/datasources | jq '.[] | select(.type=="testdata") | {name, uid}'
```

### Step 2: Update the Code

Once you have the UID, update this line in `backend/services/grafana_mcp_client.py`:

**Find this (appears multiple times):**
```python
"datasource": {"type": "testdata", "uid": "PD8C576611E62080A"},
```

**Replace with your actual UID:**
```python
"datasource": {"type": "testdata", "uid": "YOUR_ACTUAL_UID_HERE"},
```

### Step 3: Alternative - Use Datasource Name

If you don't want to hardcode the UID, you can use the datasource name instead:

```python
"datasource": {"type": "testdata"},
```

Or:

```python
"datasource": "-- Grafana --",  # Built-in testdata
```

## Quick Test

After updating, run a new experiment and check if the Grafana dashboard shows data.

## Files to Update

- `backend/services/grafana_mcp_client.py` - Lines with datasource configuration (5 places)

## Current Hardcoded UID

We're currently using: `PD8C576611E62080A`

This might not exist in your Grafana instance, which is why you see "No data".

## Alternative Solution: Use Grafana's Built-in Datasource

Instead of testdata, we can use Grafana's built-in datasource for static panels:

```python
"datasource": None,  # Use default
```

Or create panels without datasource queries (just display static values in the panel description).

Let me know your Grafana testdata datasource UID and I'll update the code!
