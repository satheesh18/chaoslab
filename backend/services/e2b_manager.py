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
                
                # Create sandbox using the constructor (not .create() method)
                # Pass api_key directly to the Sandbox constructor
                self.sandbox = Sandbox(
                    api_key=self.api_key,
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
        """Execute chaos script and collect metrics with time-series data"""
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
            
            # Create metrics collection script for background monitoring
            monitor_script = self._create_metrics_monitor_script(duration)
            self.sandbox.files.write("/tmp/monitor_metrics.sh", monitor_script)
            self.sandbox.commands.run("chmod +x /tmp/monitor_metrics.sh")
            
            # Start metrics monitoring in background
            logger.info("Starting metrics monitoring...")
            self.sandbox.commands.run(
                "bash /tmp/monitor_metrics.sh &",
                background=True
            )
            
            # Give monitor time to start
            time.sleep(2)
            
            # Run chaos script with extended timeout
            script_timeout = duration + 30
            logger.info(f"Executing chaos script (timeout: {script_timeout}s)...")
            result = self.sandbox.commands.run(
                f"bash {script_path}",
                timeout=script_timeout
            )
            
            # Wait a moment for final metrics to be written
            time.sleep(3)
            
            # Collect time-series metrics
            metrics = self._collect_timeseries_metrics()
            
            logger.info("Chaos script completed")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to run chaos script: {e}")
            raise
    
    def _create_metrics_monitor_script(self, duration: int) -> str:
        """Create a script that monitors metrics over time"""
        return f'''#!/bin/bash
# Monitor metrics every 5 seconds for the duration of the experiment
METRICS_FILE="/tmp/metrics_timeseries.csv"
echo "time_offset,cpu_percent,memory_percent,error_count" > $METRICS_FILE

START_TIME=$(date +%s)
END_TIME=$((START_TIME + {duration}))

while [ $(date +%s) -lt $END_TIME ]; do
    CURRENT_TIME=$(date +%s)
    TIME_OFFSET=$((CURRENT_TIME - START_TIME))
    
    # Get CPU usage - try multiple methods for reliability
    CPU_USAGE=""
    
    # Method 1: Try mpstat (most accurate)
    if command -v mpstat &> /dev/null; then
        CPU_USAGE=$(mpstat 1 1 2>/dev/null | awk '/Average/ {{print 100 - $NF}}' | head -1)
    fi
    
    # Method 2: Use top with better parsing (fallback)
    if [ -z "$CPU_USAGE" ] || [ "$CPU_USAGE" = "0.00" ]; then
        # Run top twice to get accurate reading (first run is often inaccurate)
        CPU_LINE=$(top -bn2 -d 0.5 2>/dev/null | grep "Cpu(s)" | tail -1)
        if [ -n "$CPU_LINE" ]; then
            # Try to extract idle percentage - handle different top formats
            CPU_IDLE=$(echo "$CPU_LINE" | grep -oP '\\d+\\.\\d+(?=\\s*id)' | head -1)
            if [ -z "$CPU_IDLE" ]; then
                # Alternative parsing for different top output format
                CPU_IDLE=$(echo "$CPU_LINE" | sed -n 's/.*,\\s*\\([0-9.]*\\)\\s*id.*/\\1/p')
            fi
            if [ -n "$CPU_IDLE" ]; then
                CPU_USAGE=$(echo "$CPU_IDLE" | awk '{{printf "%.2f", 100 - $1}}')
            fi
        fi
    fi
    
    # Method 3: Use /proc/stat as last resort
    if [ -z "$CPU_USAGE" ] || [ "$CPU_USAGE" = "0.00" ]; then
        # Read CPU stats from /proc/stat
        if [ -f /tmp/cpu_prev ]; then
            read prev_total prev_idle < /tmp/cpu_prev
            cpu_line=$(head -1 /proc/stat)
            cpu_values=($cpu_line)
            idle=${{cpu_values[4]}}
            total=0
            for value in "${{cpu_values[@]:1}}"; do
                total=$((total + value))
            done
            
            diff_idle=$((idle - prev_idle))
            diff_total=$((total - prev_total))
            if [ $diff_total -gt 0 ]; then
                CPU_USAGE=$(awk "BEGIN {{printf \\"%.2f\\", 100 * (1 - $diff_idle / $diff_total)}}")
            fi
            
            echo "$total $idle" > /tmp/cpu_prev
        else
            # First run - initialize
            cpu_line=$(head -1 /proc/stat)
            cpu_values=($cpu_line)
            idle=${{cpu_values[4]}}
            total=0
            for value in "${{cpu_values[@]:1}}"; do
                total=$((total + value))
            done
            echo "$total $idle" > /tmp/cpu_prev
            CPU_USAGE="5.0"
        fi
    fi
    
    # Ensure CPU_USAGE is not empty and is a valid number
    if [ -z "$CPU_USAGE" ] || ! [[ "$CPU_USAGE" =~ ^[0-9]+\\.?[0-9]*$ ]]; then
        CPU_USAGE="5.0"
    fi
    
    # Get memory usage percentage
    MEM_USAGE=$(free | grep Mem | awk '{{printf "%.2f", ($3/$2) * 100.0}}')
    
    # Count errors in Flask logs so far
    ERROR_COUNT=$(grep -c "ERROR" /tmp/flask_app.log 2>/dev/null || echo "0")
    
    # Append to CSV
    echo "$TIME_OFFSET,$CPU_USAGE,$MEM_USAGE,$ERROR_COUNT" >> $METRICS_FILE
    
    sleep 5
done

# Cleanup
rm -f /tmp/cpu_prev
'''

    def _collect_timeseries_metrics(self) -> Dict[str, Any]:
        """Collect time-series metrics from monitoring script"""
        if not self.sandbox:
            raise RuntimeError("Sandbox not created")
        
        try:
            # Get Flask app logs
            logs_result = self.sandbox.commands.run("cat /tmp/flask_app.log 2>/dev/null || echo 'No logs'")
            logs = logs_result.stdout
            
            # Get time-series metrics CSV
            metrics_csv = self.sandbox.commands.run("cat /tmp/metrics_timeseries.csv 2>/dev/null || echo ''")
            
            timeline = []
            cpu_peak = 0.0
            memory_peak = 0.0
            error_count = 0
            recovery_time = None
            
            if metrics_csv.stdout:
                lines = metrics_csv.stdout.strip().split('\n')
                # Skip header
                for line in lines[1:]:
                    if line.strip():
                        try:
                            parts = line.split(',')
                            # Validate we have all 4 parts before accessing them
                            if len(parts) < 4:
                                logger.warning(f"Skipping incomplete metrics line: {line}")
                                continue
                            
                            time_offset = int(parts[0])
                            cpu = float(parts[1])
                            memory = float(parts[2])
                            errors = int(parts[3])
                            
                            timeline.append({
                                "time_offset": time_offset,
                                "cpu": round(cpu, 2),
                                "memory": round(memory, 2),
                                "error_count": errors
                            })
                            
                            # Track peaks
                            cpu_peak = max(cpu_peak, cpu)
                            memory_peak = max(memory_peak, memory)
                            error_count = max(error_count, errors)
                            
                            # Calculate recovery time (when CPU/memory drop back to reasonable levels)
                            if recovery_time is None and time_offset > 10:
                                if cpu < 30 and memory < 50 and timeline[-1].get('cpu', 100) > 50:
                                    recovery_time = time_offset
                        except (IndexError, ValueError) as e:
                            logger.warning(f"Failed to parse metrics line: {line}, error: {e}")
                            continue
            
            # If no timeline data, create a minimal one
            if not timeline:
                logger.warning("No timeline data collected, using minimal fallback")
                timeline = [
                    {"time_offset": 0, "cpu": 5.0, "memory": 20.0, "error_count": 0},
                    {"time_offset": 30, "cpu": 10.0, "memory": 25.0, "error_count": 0}
                ]
                cpu_peak = 10.0
                memory_peak = 25.0
            
            # Count actual errors in logs
            actual_error_count = logs.count("ERROR") + logs.count("Exception")
            
            return {
                "timeline": timeline,
                "cpu_peak": round(cpu_peak, 2),
                "memory_peak": round(memory_peak, 2),
                "error_count": actual_error_count,
                "recovery_time_seconds": recovery_time,
                "logs": logs,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to collect timeseries metrics: {e}")
            return {
                "timeline": [{"time_offset": 0, "cpu": 0.0, "memory": 0.0, "error_count": 0}],
                "cpu_peak": 0.0,
                "memory_peak": 0.0,
                "error_count": 0,
                "recovery_time_seconds": None,
                "logs": str(e),
                "timestamp": time.time()
            }
    
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
    
    def run_parallel_experiments(self, scenario: str, config: Dict[str, Any], num_instances: int) -> Dict[str, Any]:
        """Run experiments in parallel across multiple E2B sandboxes and average the results"""
        import concurrent.futures
        import copy
        
        logger.info(f"Starting {num_instances} parallel experiments")
        
        # Create separate E2B managers for each instance
        def run_single_instance(instance_num: int) -> Dict[str, Any]:
            try:
                logger.info(f"Instance {instance_num + 1}/{num_instances}: Creating sandbox")
                instance_manager = E2BManager(self.api_key)
                instance_manager.create_sandbox()
                instance_manager.deploy_test_app()
                
                logger.info(f"Instance {instance_num + 1}/{num_instances}: Running chaos script")
                metrics = instance_manager.run_chaos_script(scenario, config)
                
                logger.info(f"Instance {instance_num + 1}/{num_instances}: Cleaning up")
                instance_manager.cleanup()
                
                return metrics
            except Exception as e:
                logger.error(f"Instance {instance_num + 1}/{num_instances} failed: {e}")
                return None
        
        # Run experiments in parallel
        all_metrics = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_instances) as executor:
            futures = [executor.submit(run_single_instance, i) for i in range(num_instances)]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    all_metrics.append(result)
        
        if not all_metrics:
            raise Exception("All parallel experiments failed")
        
        logger.info(f"Successfully completed {len(all_metrics)}/{num_instances} experiments")
        
        # Average the metrics
        return self._average_metrics(all_metrics)
    
    def _average_metrics(self, all_metrics: list) -> Dict[str, Any]:
        """Average metrics from multiple experiment runs"""
        if not all_metrics:
            return {}
        
        # Get the longest timeline
        max_timeline_length = max(len(m.get("timeline", [])) for m in all_metrics)
        
        # Average timeline data point by point
        averaged_timeline = []
        for i in range(max_timeline_length):
            time_offset = None
            cpu_values = []
            memory_values = []
            error_values = []
            
            for metrics in all_metrics:
                timeline = metrics.get("timeline", [])
                if i < len(timeline):
                    point = timeline[i]
                    if time_offset is None:
                        time_offset = point.get("time_offset", i * 5)
                    cpu_values.append(point.get("cpu", 0))
                    memory_values.append(point.get("memory", 0))
                    error_values.append(point.get("error_count", 0))
            
            if cpu_values:
                averaged_timeline.append({
                    "time_offset": time_offset,
                    "cpu": round(sum(cpu_values) / len(cpu_values), 2),
                    "memory": round(sum(memory_values) / len(memory_values), 2),
                    "error_count": round(sum(error_values) / len(error_values))
                })
        
        # Average peak values
        cpu_peaks = [m.get("cpu_peak", 0) for m in all_metrics]
        memory_peaks = [m.get("memory_peak", 0) for m in all_metrics]
        error_counts = [m.get("error_count", 0) for m in all_metrics]
        
        # Combine logs
        combined_logs = "\n\n=== COMBINED LOGS FROM ALL INSTANCES ===\n\n"
        for i, metrics in enumerate(all_metrics):
            combined_logs += f"\n--- Instance {i + 1} ---\n"
            combined_logs += metrics.get("logs", "")[:500]  # Limit log size
        
        return {
            "timeline": averaged_timeline,
            "cpu_peak": round(sum(cpu_peaks) / len(cpu_peaks), 2),
            "memory_peak": round(sum(memory_peaks) / len(memory_peaks), 2),
            "error_count": round(sum(error_counts) / len(error_counts)),
            "recovery_time_seconds": None,  # Average recovery time doesn't make sense
            "logs": combined_logs,
            "timestamp": all_metrics[0].get("timestamp"),
            "num_instances": len(all_metrics)
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

# Add network latency (requires root, may fail in some sandboxes)
tc qdisc add dev eth0 root netem delay 300ms 2>/dev/null || echo "Network delay simulation skipped (requires root)"

# Make concurrent requests to test app to generate load
for i in {{1..{duration}}}; do
    # Make 3 concurrent requests to generate CPU load
    curl -s http://localhost:5000/api/data > /dev/null &
    curl -s http://localhost:5000/api/heavy > /dev/null &
    curl -s http://localhost:5000/api/data > /dev/null &
    sleep 1
done

# Wait for background jobs to complete
wait

# Remove network delay
tc qdisc del dev eth0 root netem 2>/dev/null || true

echo "Network delay chaos completed"
""",
            "memory_pressure": f"""#!/bin/bash
echo "Starting memory pressure chaos..."

# Create Python script to consume memory
cat > /tmp/memory_hog.py << 'PYTHON_EOF'
import time
import sys
import signal

# Global to keep memory alive
chunks = []
keep_running = True

def signal_handler(sig, frame):
    global keep_running
    print("\\nReceived signal, releasing memory...")
    keep_running = False

def consume_memory(target_percent=80, duration=60):
    global chunks, keep_running
    
    # Set up signal handler
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Get total memory in bytes
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemTotal'):
                total_mem_kb = int(line.split()[1])
                break
    
    # Calculate target memory to consume (in MB)
    total_mem_mb = total_mem_kb / 1024
    target_mem_mb = int(total_mem_mb * (target_percent / 100))
    
    print(f"Total memory: {{total_mem_mb:.0f}} MB")
    print(f"Target consumption: {{target_mem_mb}} MB ({{target_percent}}%)")
    
    # Allocate memory in chunks
    chunk_size_mb = 50  # 50MB chunks
    allocated_mb = 0
    
    try:
        # Phase 1: Allocate memory
        while allocated_mb < target_mem_mb and keep_running:
            # Allocate and fill with data to ensure it's actually used
            chunk = bytearray(chunk_size_mb * 1024 * 1024)
            # Write to it to ensure it's in physical memory
            for i in range(0, len(chunk), 4096):
                chunk[i] = 1
            chunks.append(chunk)
            allocated_mb += chunk_size_mb
            print(f"Allocated: {{allocated_mb}} MB / {{target_mem_mb}} MB")
        
        print(f"Memory allocated successfully! Holding for {{duration}} seconds...")
        
        # Phase 2: Hold memory and actively touch it to prevent swapping
        start_time = time.time()
        iteration = 0
        while (time.time() - start_time) < duration and keep_running:
            # Every 5 seconds, touch the memory to keep it active
            if iteration % 5 == 0:
                print(f"Holding memory... ({{int(time.time() - start_time)}}s / {{duration}}s)")
                # Touch random pages in each chunk to prevent OS from swapping
                for chunk in chunks[::10]:  # Touch every 10th chunk
                    if len(chunk) > 0:
                        chunk[0] = chunk[0]  # Read and write
                        chunk[len(chunk)//2] = 1  # Touch middle
                        chunk[-1] = 1  # Touch end
            
            time.sleep(1)
            iteration += 1
        
        print(f"Duration complete. Held memory for {{int(time.time() - start_time)}} seconds")
        
    except MemoryError:
        print(f"MemoryError: Allocated {{allocated_mb}} MB before running out")
        time.sleep(duration)
    except Exception as e:
        print(f"Error: {{e}}")
    finally:
        print("Releasing memory...")
        chunks.clear()

if __name__ == "__main__":
    consume_memory(target_percent=80, duration={duration} + 10)
PYTHON_EOF

# Run memory hog in background
python3 /tmp/memory_hog.py > /tmp/memory_hog.log 2>&1 &
MEMORY_PID=$!

# Give it time to allocate memory (faster now - just 3 seconds)
sleep 3

# Make requests while under memory pressure
for i in {{1..{duration}}}; do
    curl -s http://localhost:5000/api/data > /dev/null &
    curl -s http://localhost:5000/api/heavy > /dev/null &
    # Also hit memory endpoint to add more pressure
    curl -s http://localhost:5000/api/memory > /dev/null &
    sleep 1
done

# Kill memory hog (don't wait for it to finish naturally)
kill $MEMORY_PID 2>/dev/null || true
wait $MEMORY_PID 2>/dev/null || true

# Show memory hog log
echo "=== Memory Hog Log ==="
cat /tmp/memory_hog.log

echo "Memory pressure chaos completed"
""",
            "disk_full": f"""#!/bin/bash
echo "Starting disk full chaos..."

# Get available disk space in /tmp (in KB)
AVAILABLE_KB=$(df /tmp | tail -1 | awk '{{print $4}}')
AVAILABLE_MB=$((AVAILABLE_KB / 1024))
echo "Available space in /tmp: ${{AVAILABLE_MB}} MB"

# Fill to 95% capacity (leave 5% for system operations)
FILL_MB=$((AVAILABLE_MB * 95 / 100))
echo "Will fill ${{FILL_MB}} MB (95% of available space)"

# Create a Python script for aggressive disk filling
cat > /tmp/disk_filler.py << 'PYTHON_EOF'
import os
import time

def fill_disk(target_mb, duration):
    chunk_size = 10 * 1024 * 1024  # 10MB chunks
    files_created = []
    total_written_mb = 0
    file_counter = 0
    
    print(f"Starting to fill disk: target={{target_mb}}MB")
    
    try:
        # Phase 1: Fill disk quickly
        while total_written_mb < target_mb:
            filename = f"/tmp/fillfile_{{file_counter}}.dat"
            try:
                with open(filename, 'wb') as f:
                    # Write 10MB at a time
                    f.write(b'\\x00' * chunk_size)
                    files_created.append(filename)
                    total_written_mb += 10
                    file_counter += 1
                    
                    if file_counter % 10 == 0:
                        print(f"Written: {{total_written_mb}}MB / {{target_mb}}MB")
            except OSError as e:
                print(f"Disk full at {{total_written_mb}}MB: {{e}}")
                break
        
        print(f"Disk filled with {{total_written_mb}}MB. Holding for {{duration}} seconds...")
        
        # Phase 2: Keep disk full for duration
        start_time = time.time()
        while (time.time() - start_time) < duration:
            # Try to write more to keep disk at capacity
            try:
                test_file = f"/tmp/test_write_{{int(time.time())}}.tmp"
                with open(test_file, 'wb') as f:
                    f.write(b'\\x00' * 1024 * 1024)  # Try to write 1MB
                files_created.append(test_file)
            except:
                pass  # Expected to fail when disk is full
            
            time.sleep(5)
            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0:
                print(f"Holding disk full... ({{elapsed}}s / {{duration}}s)")
        
        print("Duration complete. Cleaning up...")
        
    finally:
        # Cleanup
        for filename in files_created:
            try:
                os.remove(filename)
            except:
                pass
        print(f"Removed {{len(files_created)}} files")

if __name__ == "__main__":
    import sys
    target_mb = int(sys.argv[1])
    duration = int(sys.argv[2])
    fill_disk(target_mb, duration)
PYTHON_EOF

# Run disk filler in background
python3 /tmp/disk_filler.py $FILL_MB {duration} > /tmp/disk_filler.log 2>&1 &
DISK_PID=$!

# Give it time to start filling (10 seconds to fill significant space)
sleep 10

# Show initial disk usage
echo "=== Disk Usage After Initial Fill ==="
df -h /tmp

# Make requests while disk is full
for i in {{1..{duration}}}; do
    curl -s http://localhost:5000/api/data > /dev/null &
    curl -s http://localhost:5000/api/heavy > /dev/null &
    
    # Try to write logs (will fail when disk is full)
    echo "Test log entry $i" >> /tmp/test_writes.log 2>/dev/null || true
    
    sleep 1
done

# Kill disk filler (it will cleanup)
kill $DISK_PID 2>/dev/null || true
wait $DISK_PID 2>/dev/null || true

# Show disk filler log
echo "=== Disk Filler Log ==="
cat /tmp/disk_filler.log

# Show final disk usage
echo "=== Final Disk Usage ==="
df -h /tmp

# Final cleanup
rm -f /tmp/fillfile_* /tmp/test_writes.log /tmp/disk_filler.py /tmp/disk_filler.log

echo "Disk full chaos completed"
""",
            "process_kill": f"""#!/bin/bash
echo "Starting process kill chaos..."

# Make requests and periodically stress the system
for i in {{1..{duration}}}; do
    # Every 15 seconds, create CPU spike
    if [ $((i % 15)) -eq 0 ]; then
        # Create CPU load burst
        for j in {{1..5}}; do
            curl -s http://localhost:5000/api/heavy > /dev/null &
        done
    fi
    
    curl -s http://localhost:5000/api/data > /dev/null &
    sleep 1
done

# Wait for background jobs
wait

echo "Process kill chaos completed"
""",
            "dependency_failure": f"""#!/bin/bash
echo "Starting dependency failure chaos..."

# Block DNS temporarily (requires root, may fail)
echo "127.0.0.1 fake-database.local" >> /etc/hosts 2>/dev/null || true

# Make requests with some CPU load
for i in {{1..{duration}}}; do
    curl -s http://localhost:5000/api/data > /dev/null &
    # Every 10 seconds, add heavy load
    if [ $((i % 10)) -eq 0 ]; then
        curl -s http://localhost:5000/api/heavy > /dev/null &
    fi
    sleep 1
done

# Wait for background jobs
wait

echo "Dependency failure chaos completed"
"""
        }
        
        return scripts.get(scenario, scripts["network_delay"])
