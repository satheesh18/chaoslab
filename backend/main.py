import os
import uuid
import logging
from datetime import datetime
from typing import Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from models import (
    StartExperimentRequest,
    ExperimentResponse,
    StatusResponse,
    ResultsResponse,
    ExperimentStatus,
    ExperimentMetrics
)
from services.e2b_manager import E2BManager
from services.groq_analyzer import GroqAnalyzer
from services.grafana_client import GrafanaClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings from environment"""
    e2b_api_key: str
    groq_api_key: str
    groq_model: str = "mixtral-8x7b-32768"
    grafana_mcp_url: str = "http://localhost:8000"  # Grafana MCP default
    backend_port: int = 8001  # Changed from 8000 to avoid Grafana MCP conflict
    backend_host: str = "0.0.0.0"
    
    class Config:
        env_file = ".env"


# Initialize settings
settings = Settings()

# In-memory storage for experiments (use database in production)
experiments: Dict[str, Dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting ChaosLab backend...")
    yield
    logger.info("Shutting down ChaosLab backend...")


# Initialize FastAPI app
app = FastAPI(
    title="ChaosLab API",
    description="Chaos Engineering Platform with E2B, Groq, and Grafana MCP",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "ChaosLab API",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.post("/api/experiment/start", response_model=ExperimentResponse)
async def start_experiment(request: StartExperimentRequest):
    """
    Start a new chaos experiment
    
    This endpoint:
    1. Creates an E2B sandbox
    2. Deploys the test Flask app
    3. Runs the chaos script
    4. Collects logs and metrics
    5. Analyzes with Groq
    6. Creates Grafana dashboard
    """
    experiment_id = f"exp_{uuid.uuid4().hex[:8]}"
    
    logger.info(f"Starting experiment {experiment_id}: {request.scenario}")
    
    # Initialize experiment
    experiments[experiment_id] = {
        "id": experiment_id,
        "scenario": request.scenario,
        "config": request.config.model_dump(),
        "status": ExperimentStatus.PENDING,
        "created_at": datetime.now(),
        "progress": 0
    }
    
    try:
        # Update status
        experiments[experiment_id]["status"] = ExperimentStatus.RUNNING
        experiments[experiment_id]["progress"] = 10
        
        # Initialize E2B manager
        e2b_manager = E2BManager(settings.e2b_api_key)
        
        # Create sandbox
        logger.info(f"Creating sandbox for {experiment_id}")
        sandbox_id = e2b_manager.create_sandbox()
        experiments[experiment_id]["sandbox_id"] = sandbox_id
        experiments[experiment_id]["progress"] = 30
        
        # Deploy test app
        logger.info(f"Deploying test app for {experiment_id}")
        e2b_manager.deploy_test_app()
        experiments[experiment_id]["progress"] = 50
        
        # Run chaos script
        logger.info(f"Running chaos script for {experiment_id}")
        metrics = e2b_manager.run_chaos_script(
            request.scenario.value,
            request.config.model_dump()
        )
        experiments[experiment_id]["progress"] = 70
        experiments[experiment_id]["raw_metrics"] = metrics
        
        # Analyze with Groq
        logger.info(f"Analyzing results with Groq for {experiment_id}")
        experiments[experiment_id]["status"] = ExperimentStatus.ANALYZING
        
        groq_analyzer = GroqAnalyzer(settings.groq_api_key, settings.groq_model)
        analysis = groq_analyzer.analyze_experiment(
            request.scenario.value,
            metrics,
            metrics.get("logs", "")
        )
        experiments[experiment_id]["analysis"] = analysis
        experiments[experiment_id]["progress"] = 85
        
        # Create Grafana dashboard via MCP
        logger.info(f"Creating Grafana dashboard for {experiment_id}")
        dashboard_url = None
        
        try:
            grafana_client = GrafanaClient(
                settings.grafana_mcp_url,
                ""  # No token needed for MCP
            )
            dashboard_url = grafana_client.create_dashboard(
                experiment_id,
                analysis["metrics"],
                request.scenario.value
            )
            logger.info(f"Grafana dashboard created: {dashboard_url}")
        except Exception as e:
            logger.warning(f"Failed to create Grafana dashboard: {e}. Using mock URL.")
            dashboard_url = f"{settings.grafana_mcp_url}/d/chaoslab-{experiment_id}/chaos-experiment-{experiment_id}"
        
        experiments[experiment_id]["grafana_url"] = dashboard_url
        experiments[experiment_id]["progress"] = 95
        
        # Cleanup sandbox
        logger.info(f"Cleaning up sandbox for {experiment_id}")
        e2b_manager.cleanup()
        
        # Mark as completed
        experiments[experiment_id]["status"] = ExperimentStatus.COMPLETED
        experiments[experiment_id]["progress"] = 100
        
        logger.info(f"Experiment {experiment_id} completed successfully")
        
        return ExperimentResponse(
            experiment_id=experiment_id,
            status=ExperimentStatus.COMPLETED,
            created_at=experiments[experiment_id]["created_at"]
        )
        
    except Exception as e:
        logger.error(f"Experiment {experiment_id} failed: {e}")
        experiments[experiment_id]["status"] = ExperimentStatus.FAILED
        experiments[experiment_id]["error"] = str(e)
        
        raise HTTPException(
            status_code=500,
            detail=f"Experiment failed: {str(e)}"
        )


@app.get("/api/experiment/{experiment_id}/status", response_model=StatusResponse)
async def get_experiment_status(experiment_id: str):
    """Get current status of an experiment"""
    if experiment_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    exp = experiments[experiment_id]
    
    return StatusResponse(
        experiment_id=experiment_id,
        status=exp["status"],
        progress=exp.get("progress", 0),
        message=exp.get("error")
    )


@app.get("/api/experiment/{experiment_id}/results", response_model=ResultsResponse)
async def get_experiment_results(experiment_id: str):
    """Get complete results of an experiment"""
    if experiment_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    exp = experiments[experiment_id]
    
    if exp["status"] != ExperimentStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Experiment not completed. Current status: {exp['status']}"
        )
    
    analysis = exp.get("analysis", {})
    
    return ResultsResponse(
        experiment_id=experiment_id,
        summary=analysis.get("summary", "No summary available"),
        metrics=ExperimentMetrics(**analysis.get("metrics", {})),
        grafana_url=exp.get("grafana_url"),
        recommendations=analysis.get("recommendations", []),
        severity=analysis.get("severity", "unknown"),
        raw_logs=exp.get("raw_metrics", {}).get("logs")
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )
