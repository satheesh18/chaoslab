from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ChaosScenario(str, Enum):
    """Available chaos scenarios"""
    NETWORK_DELAY = "network_delay"
    MEMORY_PRESSURE = "memory_pressure"
    DISK_FULL = "disk_full"
    PROCESS_KILL = "process_kill"
    DEPENDENCY_FAILURE = "dependency_failure"


class ExperimentConfig(BaseModel):
    """Configuration for chaos experiment"""
    duration: int = Field(default=60, description="Duration in seconds", ge=10, le=300)
    intensity: str = Field(default="medium", description="Intensity level: low, medium, high")


class StartExperimentRequest(BaseModel):
    """Request to start a new experiment"""
    scenario: ChaosScenario
    config: Optional[ExperimentConfig] = ExperimentConfig()


class ExperimentStatus(str, Enum):
    """Experiment status"""
    PENDING = "pending"
    RUNNING = "running"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExperimentResponse(BaseModel):
    """Response when starting an experiment"""
    experiment_id: str
    status: ExperimentStatus
    created_at: datetime


class StatusResponse(BaseModel):
    """Current experiment status"""
    experiment_id: str
    status: ExperimentStatus
    progress: int = Field(ge=0, le=100)
    message: Optional[str] = None


class ExperimentMetrics(BaseModel):
    """Extracted metrics from experiment"""
    cpu_peak: float = Field(description="Peak CPU usage percentage")
    memory_peak: float = Field(description="Peak memory usage percentage")
    error_count: int = Field(description="Number of errors encountered")
    recovery_time_seconds: Optional[float] = Field(default=0.0, description="Time to recover in seconds")
    latency_p95: Optional[float] = Field(default=None, description="95th percentile latency in ms")


class TimelineDataPoint(BaseModel):
    """Time-series data point"""
    time_offset: int = Field(description="Time offset from experiment start in seconds")
    cpu: float = Field(description="CPU usage percentage at this time")
    memory: float = Field(description="Memory usage percentage at this time")
    error_count: int = Field(description="Cumulative error count at this time")


class ResultsResponse(BaseModel):
    """Complete experiment results"""
    experiment_id: str
    summary: str = Field(description="AI-generated summary of what happened")
    metrics: ExperimentMetrics
    grafana_url: Optional[str] = Field(default=None, description="Grafana dashboard URL")
    recommendations: List[str] = Field(description="AI-generated recommendations")
    severity: str = Field(description="Severity level: low, medium, high")
    raw_logs: Optional[str] = Field(default=None, description="Raw logs from experiment")
    timeline: Optional[List[TimelineDataPoint]] = Field(default=None, description="Time-series metrics data")
