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
                        "content": """You are an expert chaos engineering analyst specializing in application resilience and reliability.

Your role is to analyze chaos experiment results and provide actionable insights that help developers improve their systems.

ANALYSIS GUIDELINES:
1. **Summary**: Write a clear, professional narrative (2-3 sentences) that:
   - Describes what happened during the experiment
   - Highlights key observations (CPU spikes, error patterns, recovery behavior)
   - Focuses on application behavior, not just numbers
   - Uses positive framing when the app handled chaos well

2. **Metrics**: Extract exact values from the provided data:
   - cpu_peak: Peak CPU usage percentage
   - memory_peak: Peak memory usage percentage
   - error_count: Total errors encountered
   - recovery_time_seconds: Time to recover (if applicable)
   - latency_p95: 95th percentile latency (if available)

3. **Severity Assessment**:
   - "low": App handled chaos well, minimal impact
   - "medium": Some degradation but recovered
   - "high": Significant issues, poor recovery, or cascading failures

4. **Recommendations**: Provide 3-5 specific, actionable recommendations:
   - Focus on concrete improvements (not generic advice)
   - Prioritize based on observed issues
   - Include both immediate fixes and long-term improvements
   - Reference specific metrics when relevant
   - Use technical but clear language

5. **Timeline**: Use the EXACT timeline data provided - do not modify or create fake data

Return ONLY valid JSON with this structure:
{
  "summary": "Professional narrative of what happened during the experiment",
  "metrics": {
    "cpu_peak": float,
    "memory_peak": float,
    "error_count": int,
    "recovery_time_seconds": float or null,
    "latency_p95": float or null
  },
  "timeline": [exact timeline data from input],
  "severity": "low" | "medium" | "high",
  "recommendations": [
    "Specific actionable recommendation 1",
    "Specific actionable recommendation 2",
    "Specific actionable recommendation 3"
  ]
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
        """Create detailed analysis prompt with timeline data"""
        timeline_summary = "No timeline data available"
        if metrics.get('timeline'):
            timeline_summary = f"{len(metrics['timeline'])} data points collected over {metrics['timeline'][-1].get('time_offset', 0)}s"
        
        # Scenario descriptions
        scenario_context = {
            "network_delay": "Network latency was artificially increased to test timeout handling and retry logic",
            "memory_pressure": "Memory was filled to 80% capacity to test resource management and graceful degradation",
            "disk_full": "Disk space was filled to test error handling and disk space management",
            "process_kill": "Application processes were randomly terminated to test recovery mechanisms",
            "dependency_failure": "External dependencies (DNS/DB) were made unavailable to test resilience patterns"
        }
        
        context = scenario_context.get(scenario, "Application was subjected to chaos conditions")
        
        return f"""
CHAOS EXPERIMENT ANALYSIS

Scenario: {scenario.replace('_', ' ').title()}
Context: {context}

METRICS COLLECTED:
- Peak CPU Usage: {metrics.get('cpu_peak', 0):.2f}%
- Peak Memory Usage: {metrics.get('memory_peak', 0):.2f}%
- Total Errors: {metrics.get('error_count', 0)}
- Recovery Time: {metrics.get('recovery_time_seconds', 'Not measured')} seconds
- Timeline: {timeline_summary}
- Instances: {metrics.get('num_instances', 1)} {'(averaged across parallel runs)' if metrics.get('num_instances', 1) > 1 else ''}

TIMELINE DATA (showing progression):
{str(metrics.get('timeline', [])[:5])}
... ({len(metrics.get('timeline', []))} total data points)

APPLICATION LOGS (sample):
{logs[:1000]}

ANALYSIS REQUIREMENTS:
1. Describe what happened in clear, professional language
2. Assess how well the application handled the chaos
3. Identify specific issues or good behaviors observed
4. Provide 3-5 concrete, actionable recommendations based on the data
5. Rate severity based on impact and recovery

Focus on insights that help developers improve resilience. Be specific and reference actual metrics.
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
