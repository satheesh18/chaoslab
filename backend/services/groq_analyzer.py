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
            metrics: Raw metrics collected from sandbox
            logs: Application logs
            
        Returns:
            Structured analysis with summary, metrics, and recommendations
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

Return ONLY valid JSON with this exact structure:
{
  "summary": "brief narrative of what happened",
  "metrics": {
    "cpu_peak": float,
    "memory_peak": float,
    "error_count": int,
    "recovery_time_seconds": float,
    "latency_p95": float or null
  },
  "severity": "low" | "medium" | "high",
  "recommendations": ["recommendation 1", "recommendation 2", ...]
}"""
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
        """Create detailed analysis prompt"""
        return f"""
Chaos Experiment Analysis Request

Scenario: {scenario}
Duration: {metrics.get('duration', 60)} seconds

Raw Metrics:
- CPU Usage: {metrics.get('cpu_usage', 0):.2f}%
- Memory Usage: {metrics.get('memory_usage', 0):.2f}%
- Error Count: {metrics.get('error_count', 0)}

Application Logs:
{logs[:2000]}  # Truncate to avoid token limits

Please analyze this chaos engineering experiment and provide:
1. What happened during the test
2. How the application responded
3. Key performance metrics
4. Whether the application recovered gracefully
5. Recommendations for improving resilience

Focus on practical insights that would help developers improve their application.
"""
    
    def _fallback_analysis(self, scenario: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback analysis if Groq fails"""
        logger.warning("Using fallback analysis")
        
        cpu = metrics.get('cpu_usage', 0)
        memory = metrics.get('memory_usage', 0)
        errors = metrics.get('error_count', 0)
        
        # Determine severity
        severity = "low"
        if errors > 10 or cpu > 80 or memory > 80:
            severity = "high"
        elif errors > 5 or cpu > 60 or memory > 60:
            severity = "medium"
        
        return {
            "summary": f"Application experienced {scenario.replace('_', ' ')} scenario. "
                      f"Recorded {errors} errors with peak CPU at {cpu:.1f}% and memory at {memory:.1f}%.",
            "metrics": {
                "cpu_peak": cpu,
                "memory_peak": memory,
                "error_count": errors,
                "recovery_time_seconds": 8.0,
                "latency_p95": None
            },
            "severity": severity,
            "recommendations": [
                "Implement retry logic with exponential backoff",
                "Add circuit breaker pattern for external dependencies",
                "Monitor resource usage and set up alerts",
                "Consider horizontal scaling for high load scenarios"
            ]
        }
