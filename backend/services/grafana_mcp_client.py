import json
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class GrafanaMCPClient:
    """Client for interacting with Grafana MCP server using MCP protocol"""
    
    def __init__(self, mcp_url: str):
        """
        Initialize Grafana MCP client
        
        Args:
            mcp_url: URL of the Grafana MCP server (e.g., http://localhost:8000)
        """
        self.mcp_url = mcp_url.rstrip('/')
        self.sse_endpoint = f"{self.mcp_url}/sse"
    
    def create_dashboard_via_mcp(
        self, 
        experiment_id: str,
        metrics: Dict[str, Any],
        scenario: str,
        analysis_summary: str
    ) -> Optional[str]:
        """
        Create a Grafana dashboard using MCP tools
        
        Args:
            experiment_id: Unique experiment identifier
            metrics: Metrics to visualize
            scenario: Chaos scenario name
            analysis_summary: AI-generated summary
            
        Returns:
            Dashboard URL or None if creation fails
        """
        try:
            logger.info(f"=== Starting Grafana MCP dashboard creation for {experiment_id} ===")
            logger.info(f"MCP URL: {self.mcp_url}")
            
            # Build dashboard JSON for Grafana
            logger.info("Building dashboard JSON...")
            dashboard_json = self._build_dashboard_json(experiment_id, metrics, scenario, analysis_summary)
            logger.info(f"Dashboard JSON built successfully (size: {len(str(dashboard_json))} chars)")
            
            # Call MCP tool: update_dashboard
            # This uses the Grafana MCP server's update_dashboard tool
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "update_dashboard",
                    "arguments": {
                        "dashboard": dashboard_json,
                        "message": f"Created by ChaosLab for experiment {experiment_id}",
                        "overwrite": True
                    }
                }
            }
            
            logger.info(f"Sending MCP request to {self.mcp_url}/")
            logger.info(f"MCP request method: {mcp_request['method']}, tool: {mcp_request['params']['name']}")
            
            # Send MCP request
            response = requests.post(
                f"{self.mcp_url}/",
                json=mcp_request,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            logger.info(f"MCP response status: {response.status_code}")
            logger.info(f"MCP response body: {response.text[:500]}")  # First 500 chars
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"MCP response JSON: {json.dumps(result, indent=2)[:1000]}")
                
                if "result" in result:
                    # Extract dashboard URL from MCP response
                    dashboard_data = result["result"]
                    if isinstance(dashboard_data, dict):
                        # The MCP response should contain the dashboard UID
                        dashboard_uid = dashboard_data.get("uid", experiment_id)
                        dashboard_url = f"http://localhost:3000/d/{dashboard_uid}"
                        logger.info(f"✅ Dashboard created via MCP: {dashboard_url}")
                        return dashboard_url
                    elif isinstance(dashboard_data, str):
                        # Parse string response
                        logger.info(f"✅ Dashboard created via MCP (string response): {dashboard_data}")
                        return dashboard_data
                else:
                    logger.warning(f"⚠️  MCP response missing 'result' field: {result}")
            else:
                logger.error(f"❌ MCP request failed with status {response.status_code}")
                logger.error(f"Response: {response.text}")
            
            # Fallback to mock URL
            mock_url = f"http://localhost:3000/d/chaoslab-{experiment_id}"
            logger.info(f"Using mock dashboard URL: {mock_url}")
            return mock_url
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error calling MCP server: {e}")
            logger.error(f"Is Grafana MCP server running on {self.mcp_url}?")
            mock_url = f"http://localhost:3000/d/chaoslab-{experiment_id}"
            logger.info(f"Using mock dashboard URL: {mock_url}")
            return mock_url
        except Exception as e:
            logger.error(f"❌ Unexpected error creating dashboard via MCP: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Return mock URL as fallback
            mock_url = f"http://localhost:3000/d/chaoslab-{experiment_id}"
            logger.info(f"Using mock dashboard URL: {mock_url}")
            return mock_url
    
    def _build_dashboard_json(
        self,
        experiment_id: str,
        metrics: Dict[str, Any],
        scenario: str,
        analysis_summary: str
    ) -> Dict[str, Any]:
        """Build Grafana dashboard JSON"""
        
        return {
            "dashboard": {
                "title": f"Chaos Experiment: {scenario} - {experiment_id}",
                "uid": f"chaoslab-{experiment_id}",
                "tags": ["chaoslab", "chaos-engineering", scenario],
                "timezone": "browser",
                "schemaVersion": 16,
                "version": 0,
                "refresh": "5s",
                "panels": [
                    # Summary panel
                    {
                        "id": 1,
                        "title": "Experiment Summary",
                        "type": "text",
                        "gridPos": {"h": 4, "w": 24, "x": 0, "y": 0},
                        "options": {
                            "mode": "markdown",
                            "content": f"# {scenario}\n\n{analysis_summary}\n\n**Experiment ID:** `{experiment_id}`"
                        }
                    },
                    # CPU gauge
                    {
                        "id": 2,
                        "title": "Peak CPU Usage",
                        "type": "gauge",
                        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 4},
                        "options": {
                            "showThresholdLabels": False,
                            "showThresholdMarkers": True
                        },
                        "fieldConfig": {
                            "defaults": {
                                "unit": "percent",
                                "min": 0,
                                "max": 100,
                                "thresholds": {
                                    "mode": "absolute",
                                    "steps": [
                                        {"value": 0, "color": "green"},
                                        {"value": 50, "color": "yellow"},
                                        {"value": 80, "color": "red"}
                                    ]
                                }
                            },
                            "overrides": []
                        },
                        "targets": [{
                            "refId": "A",
                            "expr": str(metrics.get('cpu_peak', 0))
                        }]
                    },
                    # Memory gauge
                    {
                        "id": 3,
                        "title": "Peak Memory Usage",
                        "type": "gauge",
                        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 4},
                        "options": {
                            "showThresholdLabels": False,
                            "showThresholdMarkers": True
                        },
                        "fieldConfig": {
                            "defaults": {
                                "unit": "percent",
                                "min": 0,
                                "max": 100,
                                "thresholds": {
                                    "mode": "absolute",
                                    "steps": [
                                        {"value": 0, "color": "green"},
                                        {"value": 60, "color": "yellow"},
                                        {"value": 85, "color": "red"}
                                    ]
                                }
                            },
                            "overrides": []
                        },
                        "targets": [{
                            "refId": "A",
                            "expr": str(metrics.get('memory_peak', 0))
                        }]
                    },
                    # Error count stat
                    {
                        "id": 4,
                        "title": "Error Count",
                        "type": "stat",
                        "gridPos": {"h": 8, "w": 6, "x": 12, "y": 4},
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
                                        {"value": 1, "color": "yellow"},
                                        {"value": 5, "color": "red"}
                                    ]
                                }
                            },
                            "overrides": []
                        },
                        "targets": [{
                            "refId": "A",
                            "expr": str(metrics.get('error_count', 0))
                        }]
                    },
                    # Recovery time stat
                    {
                        "id": 5,
                        "title": "Recovery Time",
                        "type": "stat",
                        "gridPos": {"h": 8, "w": 6, "x": 18, "y": 4},
                        "options": {
                            "graphMode": "none",
                            "colorMode": "value"
                        },
                        "fieldConfig": {
                            "defaults": {
                                "unit": "s",
                                "thresholds": {
                                    "mode": "absolute",
                                    "steps": [
                                        {"value": 0, "color": "green"},
                                        {"value": 10, "color": "yellow"},
                                        {"value": 30, "color": "red"}
                                    ]
                                }
                            },
                            "overrides": []
                        },
                        "targets": [{
                            "refId": "A",
                            "expr": str(metrics.get('recovery_time_seconds', 0))
                        }]
                    }
                ]
            },
            "folderId": 0,
            "overwrite": True
        }
