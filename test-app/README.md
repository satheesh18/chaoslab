# Flask Test App

Simple Flask application designed for chaos engineering experiments.

## Features

- **Health Check** (`/health`) - Basic health endpoint
- **Data API** (`/api/data`) - Simulates data retrieval with random failures
- **Heavy Operation** (`/api/heavy`) - CPU intensive endpoint
- **Memory Operation** (`/api/memory`) - Memory allocation test
- **Database Simulation** (`/api/database`) - Simulates DB queries with failures
- **Network Simulation** (`/api/network`) - Simulates network latency
- **Stress Test** (`/api/stress`) - Combined CPU, memory, and I/O operations

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

App will be available at http://localhost:5000

## Running with Docker

```bash
# Build the image
docker build -t chaoslab-test-app:latest .

# Run the container
docker run -p 5000:5000 chaoslab-test-app:latest
```

## Testing Endpoints

```bash
# Health check
curl http://localhost:5000/health

# Get data
curl http://localhost:5000/api/data

# Heavy operation
curl http://localhost:5000/api/heavy

# Memory operation
curl http://localhost:5000/api/memory

# Database simulation
curl http://localhost:5000/api/database

# Network simulation
curl http://localhost:5000/api/network

# Stress test
curl http://localhost:5000/api/stress
```

## Logs

Logs are written to:
- `/tmp/flask_app.log` (inside container)
- `stdout` (visible in docker logs)

## Intentional Failure Points

- `/api/data` - 10% chance of 500 error
- `/api/database` - 5% chance of 503 error
- Random processing delays on all endpoints

These failures make the app perfect for chaos testing!
