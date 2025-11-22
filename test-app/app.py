from flask import Flask, jsonify, request
import time
import random
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/flask_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@app.route('/health')
def health():
    """Health check endpoint"""
    logger.info("Health check requested")
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": time.time()
    })


@app.route('/api/data')
def get_data():
    """Simulate data retrieval with potential failures"""
    # Simulate some processing time
    processing_time = random.uniform(0.1, 0.5)
    time.sleep(processing_time)
    
    # Random chance of error (10%)
    if random.random() < 0.1:
        logger.error("Random error occurred in /api/data")
        return jsonify({"error": "Internal server error"}), 500
    
    logger.info(f"Data request successful (took {processing_time:.2f}s)")
    return jsonify({
        "data": [1, 2, 3, 4, 5],
        "timestamp": time.time(),
        "processing_time": processing_time
    })


@app.route('/api/heavy')
def heavy_operation():
    """CPU intensive operation"""
    logger.info("Heavy operation started")
    start_time = time.time()
    
    # CPU intensive calculation
    result = sum([i**2 for i in range(100000)])
    
    elapsed = time.time() - start_time
    logger.info(f"Heavy operation completed in {elapsed:.2f}s")
    
    return jsonify({
        "result": result,
        "elapsed_time": elapsed,
        "timestamp": time.time()
    })


@app.route('/api/memory')
def memory_operation():
    """Memory intensive operation"""
    logger.info("Memory operation started")
    
    # Allocate some memory
    data = [i for i in range(1000000)]
    
    logger.info(f"Memory operation completed, allocated {len(data)} items")
    
    return jsonify({
        "items_allocated": len(data),
        "timestamp": time.time()
    })


@app.route('/api/database')
def database_operation():
    """Simulate database operation"""
    logger.info("Database operation requested")
    
    # Simulate database query time
    time.sleep(random.uniform(0.05, 0.2))
    
    # Random chance of database error (5%)
    if random.random() < 0.05:
        logger.error("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 503
    
    logger.info("Database operation successful")
    return jsonify({
        "records": [
            {"id": 1, "name": "Record 1"},
            {"id": 2, "name": "Record 2"},
            {"id": 3, "name": "Record 3"}
        ],
        "timestamp": time.time()
    })


@app.route('/api/network')
def network_operation():
    """Simulate network operation"""
    logger.info("Network operation requested")
    
    # Simulate network latency
    latency = random.uniform(0.1, 0.3)
    time.sleep(latency)
    
    logger.info(f"Network operation completed with {latency:.2f}s latency")
    
    return jsonify({
        "status": "success",
        "latency": latency,
        "timestamp": time.time()
    })


@app.route('/api/stress')
def stress_test():
    """Endpoint for stress testing"""
    logger.info("Stress test endpoint called")
    
    # Simulate various operations
    operations = []
    
    # CPU work
    _ = sum([i**2 for i in range(50000)])
    operations.append("cpu")
    
    # Memory work
    data = [i for i in range(100000)]
    operations.append("memory")
    
    # I/O work
    time.sleep(0.1)
    operations.append("io")
    
    logger.info(f"Stress test completed: {operations}")
    
    return jsonify({
        "operations": operations,
        "timestamp": time.time()
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.path}")
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    logger.info("Flask test app starting...")
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False  # Disable debug mode for chaos testing
    )
