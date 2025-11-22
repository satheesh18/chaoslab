# 🔧 CORS Error - Fixed!

## Changes Made

### 1. Backend CORS Configuration ([main.py](file:///Users/satheesh/e2b_docker/backend/main.py))

Updated CORS middleware to explicitly allow localhost origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Frontend dev server
        "http://127.0.0.1:5173",  # Alternative localhost
        "http://localhost:3000",  # Grafana
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

### 2. Frontend API Client ([client.ts](file:///Users/satheesh/e2b_docker/frontend/src/api/client.ts))

Fixed two issues:
- Updated default API URL from `8000` → `8001`
- Added `withCredentials: true` for CORS

```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,  // Enable credentials for CORS
});
```

## How to Apply the Fix

**You need to restart both backend and frontend:**

### 1. Restart Backend
```bash
# Stop the backend (Ctrl+C)
# Then restart:
cd backend
python main.py
```

### 2. Restart Frontend
```bash
# Stop the frontend (Ctrl+C)
# Then restart:
cd frontend
npm run dev
```

## Testing

After restarting, test the connection:

```bash
# 1. Check backend is running
curl http://localhost:8001/

# Should return:
# {"service":"ChaosLab API","status":"healthy","version":"1.0.0"}

# 2. Open frontend
open http://localhost:5173

# 3. Try starting an experiment
# - Select a chaos scenario
# - Click "Start Chaos Experiment"
# - Should work without CORS error!
```

## What Was the Issue?

1. **Wrong port**: Frontend was trying to call port 8000 instead of 8001
2. **Missing credentials**: CORS requests with credentials need `withCredentials: true`
3. **Preflight handling**: Needed explicit OPTIONS method in CORS config

## If You Still Get CORS Errors

Check these:

1. **Backend is running on port 8001**
   ```bash
   lsof -i :8001
   ```

2. **Frontend is running on port 5173**
   ```bash
   lsof -i :5173
   ```

3. **Check browser console** for the exact error message

4. **Clear browser cache** and hard reload (Cmd+Shift+R on Mac)

5. **Check .env file** has correct values:
   ```bash
   VITE_API_URL=http://localhost:8001
   BACKEND_PORT=8001
   ```

## You're All Set! ✅

The CORS issue should be resolved now. Just restart both servers and try again!
