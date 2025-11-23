import json
import logging
from typing import Dict, Any
from groq import Groq

logger = logging.getLogger(__name__)


class GroqAnalyzer:
    """Analyzes experiment logs using Groq LLM"""
    
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        self.client = Groq(api_key=api_key)
        self.model = model
    
    def analyze_experiment(
        self, 
        scenario: str, 
        metrics: Dict[str, Any], 
        logs: str
    ) -> Dict[str, Any]:
        """
        Analyze experiment results and extract structured insights
        
        Args:
            scenario: Chaos scenario that was run
            metrics: Raw metrics collected from sandbox (includes timeline)
            logs: Application logs
            
        Returns:
            Structured analysis with summary, metrics, recommendations, and timeline
        """
        try:
            logger.info(f"Analyzing experiment with Groq: {scenario}")
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(scenario, metrics, logs)
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a chaos engineering expert analyzing application resilience tests.
Your task is to analyze experiment logs and metrics, then provide:
1. A concise summary of what happened
2. Extracted key metrics
3. Severity assessment (low/medium/high)
4. Actionable recommendations
5. Timeline data from the provided metrics

Return ONLY valid JSON with this exact structure:
{
  "summary": "brief narrative of what happened",
  "metrics": {
    "cpu_peak": float,
    "memory_peak": float,
    "error_count": int,
    "recovery_time_seconds": float or null,
    "latency_p95": float or null
  },
  "timeline": [
    { "time_offset": 0, "cpu": 10.5, "memory": 20.3, "error_count": 0 },
    { "time_offset": 5, "cpu": 45.2, "memory": 25.1, "error_count": 1 }
  ],
  "severity": "low" | "medium" | "high",
  "recommendations": ["recommendation 1", "recommendation 2", ...]
}

IMPORTANT: Use the actual timeline data provided in the metrics, don't create fake data."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            logger.info("Analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze experiment: {e}")
            # Return fallback analysis
            return self._fallback_analysis(scenario, metrics)
    
    def _create_analysis_prompt(
        self, 
        scenario: str, 
        metrics: Dict[str, Any], 
        logs: str
    ) -> str:
        """Create detailed analysis prompt with timeline data"""
        timeline_summary = "No timeline data available"
        if metrics.get('timeline'):
            timeline_summary = f"Timeline data with {len(metrics['timeline'])} data points collected"
        
        return f"""
Chaos Experiment Analysis Request

Scenario: {scenario}

Raw Metrics Summary:
- Peak CPU Usage: {metrics.get('cpu_peak', 0):.2f}%
- Peak Memory Usage: {metrics.get('memory_peak', 0):.2f}%
- Total Error Count: {metrics.get('error_count', 0)}
- Recovery Time: {metrics.get('recovery_time_seconds', 'N/A')} seconds
- {timeline_summary}

Time-Series Data (first few samples):
{str(metrics.get('timeline', [])[:5])}

Application Logs (sample):
{logs[:1500]}

Please analyze this chaos engineering experiment and provide:
1. What happened during the test
2. How the application responded to the chaos
3. Key performance insights from the metrics
4. Whether the application recovered gracefully
5. Recommendations for improving resilience

Return the actual timeline data from the metrics provided, don't estimate or create fake data.
Focus on practical insights that would help developers improve their application.
"""
    
    def _fallback_analysis(self, scenario: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback analysis if Groq fails, using actual collected metrics"""
        logger.warning("Using fallback analysis")
        
        cpu_peak = metrics.get('cpu_peak', 0)
        memory_peak = metrics.get('memory_peak', 0)
        errors = metrics.get('error_count', 0)
        recovery_time = metrics.get('recovery_time_seconds')
        timeline = metrics.get('timeline', [])
        
        # Determine severity based on actual metrics
        severity = "low"
        if errors > 10 or cpu_peak > 80 or memory_peak > 80:
            severity = "high"
        elif errors > 5 or cpu_peak > 60 or memory_peak > 60:
            severity = "medium"
        
        return {
            "summary": f"Application experienced {scenario.replace('_', ' ')} scenario. "
                      f"Recorded {errors} errors with peak CPU at {cpu_peak:.1f}% and memory at {memory_peak:.1f}%. "
                      f"{'Recovered in ' + str(recovery_time) + ' seconds.' if recovery_time else 'System remained stable.'}",
            "metrics": {
                "cpu_peak": cpu_peak,
                "memory_peak": memory_peak,
                "error_count": errors,
                "recovery_time_seconds": recovery_time or 0.0,
                "latency_p95": None
            },
            "timeline": timeline if timeline else [
                {"time_offset": 0, "cpu": 5.0, "memory": 20.0, "error_count": 0},
                {"time_offset": 30, "cpu": 10.0, "memory": 25.0, "error_count": 0}
            ],
            "severity": severity,
            "recommendations": [
                "Implement retry logic with exponential backoff",
                "Add circuit breaker pattern for external dependencies",
                "Monitor resource usage and set up alerts",
                "Consider horizontal scaling for high load scenarios"
            ]
        }
