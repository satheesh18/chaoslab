# 🐳 Building the Test App Docker Image

The test app can run either directly in E2B or as a Docker container.

## Option 1: Direct Deployment (Current Implementation)

The E2B manager currently deploys the Flask app **directly** without Docker:
- Faster for hackathon demos
- No Docker image build required
- App code is embedded in `e2b_manager.py`

## Option 2: Docker Deployment (Production Ready)

For production use, build and use the Docker image:

### Build the Image

```bash
cd test-app

# Build the image
docker build -t chaoslab-test-app:latest .

# Test locally
docker run -p 5000:5000 chaoslab-test-app:latest

# Test endpoints
./test_endpoints.sh
```

### Push to Registry (Optional)

```bash
# Tag for Docker Hub
docker tag chaoslab-test-app:latest yourusername/chaoslab-test-app:latest

# Push to Docker Hub
docker push yourusername/chaoslab-test-app:latest

# Update .env
TEST_APP_IMAGE=yourusername/chaoslab-test-app:latest
```

### Use in E2B

To use the Docker image in E2B, you would need to modify `e2b_manager.py`:

```python
def deploy_test_app(self, image: str = "chaoslab-test-app:latest"):
    """Deploy Flask test app in sandbox using Docker"""
    if not self.sandbox:
        raise RuntimeError("Sandbox not created")
    
    try:
        logger.info(f"Deploying test app: {image}")
        
        # Install Docker
        self.sandbox.commands.run("apt-get update && apt-get install -y docker.io")
        
        # Pull and run the image
        self.sandbox.commands.run(f"docker pull {image}")
        self.sandbox.commands.run(f"docker run -d -p 5000:5000 {image}")
        
        # Wait for app to start
        time.sleep(5)
        
        logger.info("Test app deployed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to deploy test app: {e}")
        raise
```

## Current Implementation

For the hackathon, we're using **Option 1** (direct deployment) because:
- ✅ Faster startup time
- ✅ No Docker image build required
- ✅ Simpler for demos
- ✅ Same functionality

The test app code is in [`test-app/app.py`](file:///Users/satheesh/e2b_docker/test-app/app.py) and gets deployed directly to the E2B sandbox.

## Test App Features

The Flask app includes:
- `/health` - Health check
- `/api/data` - Data retrieval (10% failure rate)
- `/api/heavy` - CPU intensive operation
- `/api/memory` - Memory allocation
- `/api/database` - DB simulation (5% failure rate)
- `/api/network` - Network latency simulation
- `/api/stress` - Combined stress test

All endpoints log to `/tmp/flask_app.log` for chaos analysis.

## Testing Locally

```bash
# Run without Docker
cd test-app
pip install -r requirements.txt
python app.py

# Run with Docker
docker build -t chaoslab-test-app:latest .
docker run -p 5000:5000 chaoslab-test-app:latest

# Test all endpoints
./test_endpoints.sh
```

## Next Steps

For production deployment:
1. Build the Docker image
2. Push to a container registry
3. Update `e2b_manager.py` to use Docker deployment
4. Update `.env` with the image name

For hackathon:
- Current implementation works perfectly! ✅
- Test app is deployed directly to E2B
- No additional setup needed
