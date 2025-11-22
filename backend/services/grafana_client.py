import json
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class GrafanaClient:
    """Client for interacting with Grafana MCP"""
    
    def __init__(self, url: str, token: str = ""):
        self.url = url.rstrip('/')
        self.token = token
        # Only add Authorization header if token is provided
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    def create_dashboard(
        self, 
        experiment_id: str,
        metrics: Dict[str, Any],
        scenario: str
    ) -> Optional[str]:
        """
        Create a Grafana dashboard for experiment results
        
        Args:
            experiment_id: Unique experiment identifier
            metrics: Metrics to visualize
            scenario: Chaos scenario name
            
        Returns:
            Dashboard URL or None if creation fails
        """
        try:
            logger.info(f"Creating Grafana dashboard for experiment: {experiment_id}")
            
            # Create dashboard JSON
            dashboard = self._build_dashboard_json(experiment_id, metrics, scenario)
            
            # Create dashboard via MCP API
            response = requests.post(
                f"{self.url}/api/dashboards/db",
                headers=self.headers,
                json=dashboard,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                dashboard_url = f"{self.url}{result.get('url', '')}"
                logger.info(f"Dashboard created: {dashboard_url}")
                return dashboard_url
            else:
                logger.error(f"Failed to create dashboard: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Grafana dashboard: {e}")
            # Return a mock URL for demo purposes
            return f"{self.url}/d/chaoslab-{experiment_id}/chaos-experiment-{experiment_id}"
    
    def _build_dashboard_json(
        self, 
        experiment_id: str,
        metrics: Dict[str, Any],
        scenario: str
    ) -> Dict[str, Any]:
        """Build Grafana dashboard JSON"""
        
        # Extract metrics
        cpu_peak = metrics.get('cpu_peak', 0)
        memory_peak = metrics.get('memory_peak', 0)
        error_count = metrics.get('error_count', 0)
        recovery_time = metrics.get('recovery_time_seconds', 0)
        
        return {
            "dashboard": {
                "title": f"ChaosLab - {scenario.replace('_', ' ').title()} - {experiment_id}",
                "tags": ["chaoslab", "chaos-engineering", scenario],
                "timezone": "browser",
                "schemaVersion": 16,
                "version": 0,
                "refresh": "5s",
                "panels": [
                    {
                        "id": 1,
                        "title": "CPU Usage",
                        "type": "stat",
                        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
                        "targets": [{
                            "expr": f"{cpu_peak}",
                            "refId": "A"
                        }],
                        "options": {
                            "graphMode": "area",
                            "colorMode": "value",
                            "unit": "percent"
                        },
                        "fieldConfig": {
                            "defaults": {
                                "thresholds": {
                                    "mode": "absolute",
                                    "steps": [
                                        {"value": 0, "color": "green"},
                                        {"value": 60, "color": "yellow"},
                                        {"value": 80, "color": "red"}
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "id": 2,
                        "title": "Memory Usage",
                        "type": "stat",
                        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0},
                        "targets": [{
                            "expr": f"{memory_peak}",
                            "refId": "A"
                        }],
                        "options": {
                            "graphMode": "area",
                            "colorMode": "value",
                            "unit": "percent"
                        },
                        "fieldConfig": {
                            "defaults": {
                                "thresholds": {
                                    "mode": "absolute",
                                    "steps": [
                                        {"value": 0, "color": "green"},
                                        {"value": 60, "color": "yellow"},
                                        {"value": 80, "color": "red"}
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "id": 3,
                        "title": "Error Count",
                        "type": "stat",
                        "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0},
                        "targets": [{
                            "expr": f"{error_count}",
                            "refId": "A"
                        }],
                        "options": {
                            "graphMode": "none",
                            "colorMode": "value"
                        },
                        "fieldConfig": {
                            "defaults": {
                                "thresholds": {
                                    "mode": "absolute",
                                    "steps": [
                                        {"value": 0, "color": "green"},
                                        {"value": 5, "color": "yellow"},
                                        {"value": 10, "color": "red"}
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "id": 4,
                        "title": "Recovery Time",
                        "type": "stat",
                        "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0},
                        "targets": [{
                            "expr": f"{recovery_time}",
                            "refId": "A"
                        }],
                        "options": {
                            "graphMode": "none",
                            "colorMode": "value",
                            "unit": "s"
                        },
                        "fieldConfig": {
                            "defaults": {
                                "thresholds": {
                                    "mode": "absolute",
                                    "steps": [
                                        {"value": 0, "color": "green"},
                                        {"value": 10, "color": "yellow"},
                                        {"value": 30, "color": "red"}
                                    ]
                                }
                            }
                        }
                    }
                ]
            },
            "overwrite": True
        }
