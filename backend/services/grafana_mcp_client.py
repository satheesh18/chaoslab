import json
import logging
import time
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
        self.mcp_endpoint = f"{self.mcp_url}/mcp"
        self.session_id = None
        self.testdata_uid = None
        self._initialize_session()
        self._get_testdata_datasource()
    
    def _get_testdata_datasource(self):
        """Get the testdata datasource UID from Grafana"""
        try:
            # Try to get datasources from Grafana API
            response = requests.get("http://localhost:3000/api/datasources", timeout=5)
            if response.status_code == 200:
                datasources = response.json()
                for ds in datasources:
                    if ds.get("type") == "testdata":
                        self.testdata_uid = ds.get("uid")
                        logger.info(f"Found testdata datasource UID: {self.testdata_uid}")
                        return
            
            # Fallback to common default
            self.testdata_uid = "PD8C576611E62080A"
            logger.warning(f"Using default testdata UID: {self.testdata_uid}")
        except Exception as e:
            logger.warning(f"Could not get testdata datasource: {e}")
            self.testdata_uid = "PD8C576611E62080A"
    
    def _initialize_session(self):
        """Initialize MCP session for streamable-http transport"""
        try:
            logger.info("Initializing MCP session...")
            
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "chaoslab",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = requests.post(
                self.mcp_endpoint,
                json=init_request,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                # Extract session ID from response headers
                self.session_id = response.headers.get("Mcp-Session-Id")
                if self.session_id:
                    logger.info(f"✅ MCP session initialized: {self.session_id}")
                else:
                    logger.warning("⚠️  No session ID in response headers")
                    logger.info(f"Response headers: {dict(response.headers)}")
            else:
                logger.error(f"❌ Failed to initialize MCP session: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Error initializing MCP session: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def create_dashboard_via_mcp(
        self, 
        experiment_id: str,
        metrics: Dict[str, Any],
        scenario: str,
        analysis_summary: str,
        timeline: list = [],
        experiment_timestamp: float = None
    ) -> Optional[str]:
        """
        Create a Grafana dashboard using MCP tools with proper data visualization
        
        Args:
            experiment_id: Unique experiment identifier
            metrics: Metrics to visualize
            scenario: Chaos scenario name
            analysis_summary: AI-generated summary
            timeline: List of timeline data points
            
        Returns:
            Dashboard URL
        """
        try:
            logger.info(f"=== Creating Grafana dashboard for {experiment_id} ===")
            logger.info(f"Timeline data points: {len(timeline) if timeline else 0}")
            logger.info(f"Metrics: CPU={metrics.get('cpu_peak')}%, Memory={metrics.get('memory_peak')}%, Errors={metrics.get('error_count')}")
            
            # Build dashboard with actual data using testdata random walk + annotations
            dashboard_json = self._build_dashboard_with_data(
                experiment_id, metrics, scenario, analysis_summary, timeline, experiment_timestamp
            )
            
            # Try to create via MCP
            if self.session_id:
                try:
                    mcp_request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "update_dashboard",
                            "arguments": {
                                "dashboard": dashboard_json,
                                "message": f"ChaosLab experiment {experiment_id}",
                                "overwrite": True
                            }
                        }
                    }
                    
                    response = requests.post(
                        self.mcp_endpoint,
                        json=mcp_request,
                        headers={
                            "Content-Type": "application/json",
                            "Mcp-Session-Id": self.session_id
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if "result" in result:
                            dashboard_uid = result["result"].get("uid", experiment_id) if isinstance(result["result"], dict) else experiment_id
                            dashboard_url = f"http://localhost:3000/d/{dashboard_uid}"
                            logger.info(f"✅ Dashboard created: {dashboard_url}")
                            return dashboard_url
                except Exception as e:
                    logger.warning(f"MCP creation failed: {e}, using direct API")
            
            # Fallback: Create directly via Grafana API
            return self._create_dashboard_direct(experiment_id, dashboard_json)
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return f"http://localhost:3000/d/{experiment_id}"
    
    def _create_dashboard_direct(self, experiment_id: str, dashboard_json: Dict) -> str:
        """Create dashboard directly via Grafana HTTP API"""
        try:
            grafana_url = "http://localhost:3000"
            api_url = f"{grafana_url}/api/dashboards/db"
            
            payload = {
                "dashboard": dashboard_json,
                "overwrite": True,
                "message": f"ChaosLab experiment {experiment_id}"
            }
            
            # Try without auth first (if Grafana allows anonymous)
            response = requests.post(api_url, json=payload, timeout=10)
            
            if response.status_code in [200, 201]:
                result = response.json()
                uid = result.get("uid", experiment_id)
                dashboard_url = f"{grafana_url}/d/{uid}"
                logger.info(f"✅ Dashboard created directly: {dashboard_url}")
                return dashboard_url
            else:
                logger.warning(f"Direct API failed: {response.status_code} - {response.text[:200]}")
                return f"{grafana_url}/d/{experiment_id}"
                
        except Exception as e:
            logger.error(f"Direct API error: {e}")
            return f"http://localhost:3000/d/{experiment_id}"
    
    def _build_ascii_chart(self, timeline: list, chart_type: str) -> str:
        """Build ASCII/Unicode bar chart for visualizing timeline data"""
        if not timeline:
            return "No data available"
        
        if chart_type == "cpu_memory":
            chart = "```\n"
            chart += "CPU & Memory Usage (%)\n"
            chart += "━" * 60 + "\n\n"
            
            for point in timeline:
                time_offset = point.get("time_offset", 0)
                cpu = point.get("cpu", 0)
                mem = point.get("memory", 0)
                
                # Create bars using block characters
                cpu_bar = "█" * int(cpu / 2) + "░" * (50 - int(cpu / 2))
                mem_bar = "█" * int(mem / 2) + "░" * (50 - int(mem / 2))
                
                chart += f"{time_offset:3d}s │ CPU {cpu:5.1f}% │{cpu_bar[:25]}│\n"
                chart += f"     │ MEM {mem:5.1f}% │{mem_bar[:25]}│\n"
                chart += "     │" + "─" * 35 + "│\n"
            
            chart += "```\n"
            chart += "\n🔵 CPU Usage  🟢 Memory Usage"
            return chart
            
        else:  # errors
            chart = "```\n"
            chart += "Error Count Over Time\n"
            chart += "━" * 40 + "\n\n"
            
            max_errors = max([p.get("error_count", 0) for p in timeline]) or 1
            
            for point in timeline:
                time_offset = point.get("time_offset", 0)
                errors = point.get("error_count", 0)
                
                # Create bar
                bar_length = int((errors / max_errors) * 20) if max_errors > 0 else 0
                bar = "█" * bar_length
                
                # Color indicator
                indicator = "🟢" if errors == 0 else ("🟡" if errors < 5 else "🔴")
                
                chart += f"{time_offset:3d}s │ {errors:2d} {indicator} │{bar}\n"
            
            chart += "```\n"
            chart += "\n🟢 No Errors  🟡 Some Errors  🔴 Many Errors"
            return chart
    
    def _build_timeseries_csv(self, timeline: list, experiment_timestamp: float = None) -> str:
        """Build CSV content for time-series graph with proper timestamps"""
        import time
        
        if not timeline:
            return "time,CPU,Memory\n"
        
        # Use experiment timestamp or current time
        base_time = int((experiment_timestamp or time.time()) * 1000)
        
        csv = "time,CPU,Memory\n"
        for point in timeline:
            offset = point.get("time_offset", 0)
            timestamp = base_time + (offset * 1000)  # Convert to milliseconds
            cpu = point.get("cpu", 0)
            mem = point.get("memory", 0)
            csv += f"{timestamp},{cpu:.1f},{mem:.1f}\n"
        
        return csv
    
    def _build_errors_csv(self, timeline: list, experiment_timestamp: float = None) -> str:
        """Build CSV content for error count graph"""
        import time
        
        if not timeline:
            return "time,Errors\n"
        
        # Use experiment timestamp or current time
        base_time = int((experiment_timestamp or time.time()) * 1000)
        
        csv = "time,Errors\n"
        for point in timeline:
            offset = point.get("time_offset", 0)
            timestamp = base_time + (offset * 1000)
            errors = point.get("error_count", 0)
            csv += f"{timestamp},{errors}\n"
        
        return csv
    
    def _build_dashboard_with_data(
        self, 
        experiment_id: str, 
        metrics: Dict[str, Any],
        scenario: str,
        analysis_summary: str,
        timeline: list,
        experiment_timestamp: float = None
    ) -> Dict[str, Any]:
        """Build Grafana dashboard JSON with embedded data in markdown panels"""
        
        import time
        
        logger.info(f"Building dashboard with {len(timeline) if timeline else 0} data points")
        
        # Build timeline markdown table
        timeline_md = "| Time (s) | CPU (%) | Memory (%) | Errors |\n"
        timeline_md += "|----------|---------|------------|--------|\n"
        
        for point in timeline:
            offset = point.get("time_offset", 0)
            cpu = round(point.get("cpu", 0), 1)
            mem = round(point.get("memory", 0), 1)
            errors = point.get("error_count", 0)
            
            # Color code based on thresholds
            cpu_color = "🟢" if cpu < 50 else ("🟡" if cpu < 80 else "🔴")
            mem_color = "🟢" if mem < 60 else ("🟡" if mem < 85 else "🔴")
            err_color = "🟢" if errors == 0 else ("🟡" if errors < 5 else "🔴")
            
            timeline_md += f"| {offset} | {cpu_color} {cpu} | {mem_color} {mem} | {err_color} {errors} |\n"
            
        return {
            "title": f"ChaosLab: {scenario.replace('_', ' ').title()} - {experiment_id}",
            "uid": experiment_id,
            "tags": ["chaoslab", scenario],
            "timezone": "browser",
            "schemaVersion": 38,
            "version": 0,
            "refresh": "",
            "time": {
                "from": "now-1h",
                "to": "now"
            },
            "panels": [
                # Summary panel
                {
                    "id": 1,
                    "title": "Experiment Summary",
                    "type": "text",
                    "gridPos": {"h": 6, "w": 24, "x": 0, "y": 0},
                    "options": {
                        "mode": "markdown",
                        "content": f"""# {scenario.replace('_', ' ').title()}

{analysis_summary}

**Experiment ID:** `{experiment_id}`  
**Peak CPU:** {metrics.get('cpu_peak', 0):.1f}%  
**Peak Memory:** {metrics.get('memory_peak', 0):.1f}%  
**Errors:** {metrics.get('error_count', 0)}  
**Recovery Time:** {metrics.get('recovery_time_seconds') or 'N/A'}s  
**Data Points:** {len(timeline)} samples

🟢 = Normal  🟡 = Warning  🔴 = Critical
"""
                    }
                },
                # CPU & Memory Visual Chart
                {
                    "id": 2,
                    "title": "CPU & Memory Usage Over Time",
                    "type": "text",
                    "gridPos": {"h": 10, "w": 16, "x": 0, "y": 6},
                    "options": {
                        "mode": "markdown",
                        "content": self._build_ascii_chart(timeline, "cpu_memory")
                    }
                },
                # Error Count Visual Chart
                {
                    "id": 3,
                    "title": "Error Count Over Time",
                    "type": "text",
                    "gridPos": {"h": 10, "w": 8, "x": 16, "y": 6},
                    "options": {
                        "mode": "markdown",
                        "content": self._build_ascii_chart(timeline, "errors")
                    }
                },
                # Timeline Data Table (below graphs)
                {
                    "id": 8,
                    "title": "Detailed Metrics",
                    "type": "text",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16},
                    "options": {
                        "mode": "markdown",
                        "content": timeline_md
                    }
                },
                # Peak CPU
                {
                    "id": 4,
                    "title": "Peak CPU Usage",
                    "type": "text",
                    "gridPos": {"h": 6, "w": 6, "x": 0, "y": 24},
                    "options": {
                        "mode": "markdown",
                        "content": f"""# {metrics.get('cpu_peak', 0):.1f}%

{'🟢 Normal' if metrics.get('cpu_peak', 0) < 50 else ('🟡 Warning' if metrics.get('cpu_peak', 0) < 80 else '🔴 Critical')}
"""
                    }
                },
                # Peak Memory
                {
                    "id": 5,
                    "title": "Peak Memory Usage",
                    "type": "text",
                    "gridPos": {"h": 6, "w": 6, "x": 6, "y": 24},
                    "options": {
                        "mode": "markdown",
                        "content": f"""# {metrics.get('memory_peak', 0):.1f}%

{'🟢 Normal' if metrics.get('memory_peak', 0) < 60 else ('🟡 Warning' if metrics.get('memory_peak', 0) < 85 else '🔴 Critical')}
"""
                    }
                },
                # Total Errors
                {
                    "id": 6,
                    "title": "Total Errors",
                    "type": "text",
                    "gridPos": {"h": 6, "w": 6, "x": 12, "y": 24},
                    "options": {
                        "mode": "markdown",
                        "content": f"""# {metrics.get('error_count', 0)}

{'🟢 No Errors' if metrics.get('error_count', 0) == 0 else ('🟡 Some Errors' if metrics.get('error_count', 0) < 5 else '🔴 Many Errors')}
"""
                    }
                },
                # Recovery Time
                {
                    "id": 7,
                    "title": "Recovery Time",
                    "type": "text",
                    "gridPos": {"h": 6, "w": 6, "x": 18, "y": 24},
                    "options": {
                        "mode": "markdown",
                        "content": f"""# {metrics.get('recovery_time_seconds') if metrics.get('recovery_time_seconds') is not None else 'N/A'}{'s' if metrics.get('recovery_time_seconds') is not None else ''}

{'🟢 Fast' if metrics.get('recovery_time_seconds') and metrics.get('recovery_time_seconds') < 10 else ('🟡 Moderate' if metrics.get('recovery_time_seconds') and metrics.get('recovery_time_seconds') < 30 else ('🔴 Slow' if metrics.get('recovery_time_seconds') else 'No Recovery'))}
"""
                    }
                }
            ]
        }
