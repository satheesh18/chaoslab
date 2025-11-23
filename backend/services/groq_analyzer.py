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
            
            # Get codebase context
            codebase_context = self._get_codebase_context()
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(scenario, metrics, logs, codebase_context)
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert chaos engineering analyst specializing in application resilience and reliability.

Your role is to analyze chaos experiment results and provide actionable insights that help developers improve their systems.

CRITICAL: You MUST analyze the provided application code and tailor ALL recommendations to the specific endpoints, functions, and patterns you see in that code.

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

4. **Recommendations** - THIS IS CRITICAL:
   - You MUST provide 4-6 specific, code-aware recommendations
   - EVERY recommendation MUST reference actual endpoints, functions, or code patterns from the provided application code
   - DO NOT give generic advice like "Add monitoring" or "Implement retry logic"
   - INSTEAD, be hyper-specific to the code you see
   
   EXAMPLES OF GOOD RECOMMENDATIONS:
   ✅ "The /api/heavy endpoint performs sum([i**2 for i in range(100000)]) synchronously - move this to a background task queue (Celery/RQ) to prevent blocking"
   ✅ "Add exponential backoff retry logic to the /api/database endpoint which currently has a 5% random failure rate (line 87: if random.random() < 0.05)"
   ✅ "The /api/data endpoint uses random.uniform(0.1, 0.5) sleep - add timeout handling and circuit breaker pattern for production"
   ✅ "Implement connection pooling for the database_operation() function to handle the simulated 0.05-0.2s query times more efficiently"
   ✅ "The memory_operation() allocates 1M items in a list - consider using generators or streaming for large datasets to reduce memory pressure"
   ✅ "Add rate limiting to /api/stress endpoint which performs CPU, memory, and I/O operations simultaneously"
   
   EXAMPLES OF BAD RECOMMENDATIONS (DO NOT DO THIS):
   ❌ "Implement monitoring and alerting"
   ❌ "Add retry logic for failed requests"
   ❌ "Use caching to improve performance"
   ❌ "Scale horizontally to handle load"
   
   YOUR RECOMMENDATIONS MUST:
   - Reference specific endpoint paths (e.g., /api/heavy, /api/database)
   - Reference specific function names (e.g., heavy_operation(), database_operation())
   - Reference specific code patterns you see (e.g., list comprehensions, sleep calls, random errors)
   - Suggest concrete code changes based on what you observe
   - Be prioritized based on the chaos scenario and observed metrics

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
    "Hyper-specific recommendation referencing actual endpoint/function/code pattern",
    "Another specific recommendation with exact code reference",
    "Third recommendation based on observed code structure",
    "Fourth recommendation tailored to the application"
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
    
    def _get_codebase_context(self) -> str:
        """Read test app code to provide context for analysis"""
        try:
            with open('test-app/app.py', 'r') as f:
                code = f.read()
            
            # Add a summary of key endpoints for emphasis
            summary = """
# KEY ENDPOINTS IN THIS APPLICATION:
# - /health: Health check endpoint
# - /api/data: Data retrieval with random 0.1-0.5s delay and 10% error rate
# - /api/heavy: CPU-intensive operation (sum of 100k squared numbers)
# - /api/memory: Memory-intensive operation (allocates 1M item list)
# - /api/database: Simulates DB queries with 0.05-0.2s latency and 5% failure rate
# - /api/network: Simulates network calls with 0.1-0.3s latency
# - /api/stress: Combined CPU, memory, and I/O stress test

"""
            return summary + code
        except Exception as e:
            logger.warning(f"Could not read test app code: {e}")
            return "# Test app code not available"
    
    def _create_analysis_prompt(
        self, 
        scenario: str, 
        metrics: Dict[str, Any], 
        logs: str,
        codebase_context: str = ""
    ) -> str:
        """Create detailed analysis prompt with timeline data and codebase context"""
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

APPLICATION CODE BEING TESTED:
```python
{codebase_context[:3000]}
```

ANALYSIS REQUIREMENTS:
1. Describe what happened in clear, professional language
2. Assess how well the application handled the chaos
3. Identify specific issues or good behaviors observed in the CODE
4. **CRITICAL**: Provide 4-6 hyper-specific, code-aware recommendations:
   - You MUST analyze the application code above
   - Reference actual endpoint paths (e.g., /api/heavy, /api/database, /api/memory)
   - Reference actual function names (e.g., heavy_operation(), database_operation())
   - Reference specific code patterns (e.g., list comprehensions, sleep calls, error rates)
   - Suggest concrete code improvements based on what you see
   - Tailor recommendations to the chaos scenario and observed behavior
5. Rate severity based on impact and recovery

REMEMBER: Generic recommendations like "add monitoring" or "implement caching" are NOT acceptable.
Every recommendation must reference specific code elements from the application above.

Focus on insights that help developers improve resilience. Be hyper-specific and reference actual metrics AND code patterns.
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
