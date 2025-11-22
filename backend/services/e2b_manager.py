import os
import time
from typing import Dict, Any, Optional
from e2b_code_interpreter import Sandbox
import logging

logger = logging.getLogger(__name__)


class E2BManager:
    """Manages E2B sandbox lifecycle and chaos experiments"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.sandbox: Optional[Sandbox] = None
        
    def create_sandbox(self, max_retries: int = 3) -> str:
        """Create a new E2B sandbox with retry logic"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Creating E2B sandbox... (attempt {attempt + 1}/{max_retries})")
                
                # Use Sandbox.create() class method with api_key in environment
                # Set the API key as environment variable for the SDK
                os.environ['E2B_API_KEY'] = self.api_key
                
                self.sandbox = Sandbox.create(
                    timeout=120  # Timeout in seconds for code interpreter
                )
                logger.info(f"Sandbox created successfully: {self.sandbox.sandbox_id}")
                return self.sandbox.sandbox_id
                
            except Exception as e:
                last_error = e
                logger.warning(f"Sandbox creation attempt {attempt + 1} failed: {e}")
                
                # Clean up failed sandbox if it exists
                if self.sandbox:
                    try:
                        self.sandbox.kill()
                    except:
                        pass
                    self.sandbox = None
                
                # Don't retry on the last attempt
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
        
        # All retries failed
        logger.error(f"Failed to create sandbox after {max_retries} attempts: {last_error}")
        raise Exception(f"Sandbox creation failed after {max_retries} attempts: {last_error}")
    
    def deploy_test_app(self, image: str = "chaoslab-test-app:latest") -> bool:
        """Deploy Flask test app in sandbox"""
        if not self.sandbox:
            raise RuntimeError("Sandbox not created")
        
        try:
            logger.info("Deploying test app in sandbox...")
            
            # Install Python and Flask (using sudo for permissions)
            logger.info("Installing Python and Flask...")
            self.sandbox.commands.run("sudo apt-get update")
            self.sandbox.commands.run("sudo apt-get install -y python3 python3-pip curl")
            
            # Create Flask app using files.write() API
            logger.info("Creating Flask app...")
            self.sandbox.files.write(
                "/home/user/app.py",
                self._get_test_app_code()
            )
            
            # Install Flask
            self.sandbox.commands.run("pip3 install flask --break-system-packages")
            
            # Start Flask app in background
            logger.info("Starting Flask app...")
            self.sandbox.commands.run(
                "cd /home/user && nohup python3 app.py > /tmp/flask.log 2>&1 &",
                background=True
            )
            
            # Wait for app to start
            time.sleep(5)
            
            # Verify app is running
            try:
                result = self.sandbox.commands.run("curl -s http://localhost:5000/health")
                if "healthy" in result.stdout:
                    logger.info("Test app deployed and verified successfully")
                else:
                    logger.warning("App started but health check failed")
            except Exception as e:
                logger.warning(f"Health check failed: {e}, but continuing...")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy test app: {e}")
            raise
    
    def run_chaos_script(self, scenario: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute chaos script and collect metrics"""
        if not self.sandbox:
            raise RuntimeError("Sandbox not created")
        
        try:
            logger.info(f"Running chaos scenario: {scenario}")
            
            # Get chaos script
            script = self._get_chaos_script(scenario, config)
            duration = config.get("duration", 60)
            
            # Write script to sandbox using files.write()
            script_path = f"/tmp/chaos_{scenario}.sh"
            self.sandbox.files.write(script_path, script)
            
            # Make executable
            self.sandbox.commands.run(f"chmod +x {script_path}")
            
            # Run chaos script with extended timeout
            # Add buffer time for script execution (duration + 30 seconds)
            script_timeout = duration + 30
            logger.info(f"Executing chaos script (timeout: {script_timeout}s)...")
            result = self.sandbox.commands.run(
                f"bash {script_path}",
                timeout=script_timeout
            )
            
            # Collect metrics
            metrics = self._collect_metrics()
            
            logger.info("Chaos script completed")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to run chaos script: {e}")
            raise
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect system metrics and logs from sandbox"""
        if not self.sandbox:
            raise RuntimeError("Sandbox not created")
        
        try:
            # Get CPU usage
            cpu_result = self.sandbox.commands.run("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
            cpu_usage = float(cpu_result.stdout.strip().replace('%', '')) if cpu_result.stdout else 0.0
            
            # Get memory usage
            mem_result = self.sandbox.commands.run("free | grep Mem | awk '{print ($3/$2) * 100.0}'")
            mem_usage = float(mem_result.stdout.strip()) if mem_result.stdout else 0.0
            
            # Get Flask app logs
            logs_result = self.sandbox.commands.run("cat /tmp/flask_app.log 2>/dev/null || echo 'No logs'")
            logs = logs_result.stdout
            
            # Count errors in logs
            error_count = logs.count("ERROR") + logs.count("Exception")
            
            return {
                "cpu_usage": cpu_usage,
                "memory_usage": mem_usage,
                "logs": logs,
                "error_count": error_count,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "logs": str(e),
                "error_count": 0,
                "timestamp": time.time()
            }
    
    def cleanup(self):
        """Destroy sandbox and cleanup resources"""
        if self.sandbox:
            try:
                logger.info(f"Destroying sandbox: {self.sandbox.sandbox_id}")
                self.sandbox.kill()  # Use kill() for code interpreter SDK
                self.sandbox = None
                logger.info("Sandbox destroyed successfully")
            except Exception as e:
                logger.error(f"Failed to destroy sandbox: {e}")
    
    def _get_test_app_code(self) -> str:
        """Get Flask test app code"""
        return """
from flask import Flask, jsonify
import time
import random
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    filename='/tmp/flask_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/health')
def health():
    logging.info("Health check requested")
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route('/api/data')
def get_data():
    # Simulate some processing
    time.sleep(random.uniform(0.1, 0.5))
    
    # Random chance of error
    if random.random() < 0.1:
        logging.error("Random error occurred")
        return jsonify({"error": "Internal server error"}), 500
    
    logging.info("Data request successful")
    return jsonify({
        "data": [1, 2, 3, 4, 5],
        "timestamp": time.time()
    })

@app.route('/api/heavy')
def heavy_operation():
    # CPU intensive operation
    logging.info("Heavy operation started")
    result = sum([i**2 for i in range(100000)])
    logging.info("Heavy operation completed")
    return jsonify({"result": result})

if __name__ == '__main__':
    logging.info("Flask app starting...")
    app.run(host='0.0.0.0', port=5000, debug=False)
"""
    
    def _get_chaos_script(self, scenario: str, config: Dict[str, Any]) -> str:
        """Get chaos script based on scenario"""
        duration = config.get("duration", 60)
        intensity = config.get("intensity", "medium")
        
        scripts = {
            "network_delay": f"""#!/bin/bash
echo "Starting network delay chaos..."

# Add network latency
tc qdisc add dev eth0 root netem delay 300ms

# Make requests to test app
for i in {{1..{duration}}}; do
    curl -s http://localhost:5000/api/data > /dev/null
    sleep 1
done

# Remove network delay
tc qdisc del dev eth0 root netem

echo "Network delay chaos completed"
""",
            "memory_pressure": f"""#!/bin/bash
echo "Starting memory pressure chaos..."

# Allocate memory gradually
stress-ng --vm 1 --vm-bytes 80% --timeout {duration}s

echo "Memory pressure chaos completed"
""",
            "disk_full": f"""#!/bin/bash
echo "Starting disk full chaos..."

# Fill /tmp directory
dd if=/dev/zero of=/tmp/fillfile bs=1M count=1000

# Make requests
for i in {{1..{duration}}}; do
    curl -s http://localhost:5000/api/data > /dev/null
    sleep 1
done

# Cleanup
rm -f /tmp/fillfile

echo "Disk full chaos completed"
""",
            "process_kill": f"""#!/bin/bash
echo "Starting process kill chaos..."

# Get Flask PID
FLASK_PID=$(pgrep -f "python3 app.py")

# Kill and restart Flask periodically
for i in {{1..5}}; do
    sleep 10
    kill -9 $FLASK_PID
    sleep 2
    cd /app && python3 app.py &
    FLASK_PID=$(pgrep -f "python3 app.py")
done

echo "Process kill chaos completed"
""",
            "dependency_failure": f"""#!/bin/bash
echo "Starting dependency failure chaos..."

# Block DNS temporarily
echo "127.0.0.1 fake-database.local" >> /etc/hosts

# Make requests
for i in {{1..{duration}}}; do
    curl -s http://localhost:5000/api/data > /dev/null
    sleep 1
done

echo "Dependency failure chaos completed"
"""
        }
        
        return scripts.get(scenario, scripts["network_delay"])
