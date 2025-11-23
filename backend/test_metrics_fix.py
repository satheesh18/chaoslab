#!/usr/bin/env python3
"""
Test script to verify metrics collection and Grafana dashboard fixes
"""
import json
from pathlib import Path

def analyze_experiment_results():
    """Analyze stored experiment results to check data quality"""
    results_dir = Path("experiment_results")
    
    if not results_dir.exists():
        print("❌ No experiment_results directory found")
        return
    
    result_files = list(results_dir.glob("*.json"))
    print(f"📊 Found {len(result_files)} experiment results\n")
    
    issues = []
    
    for result_file in result_files:
        with open(result_file) as f:
            data = json.load(f)
        
        exp_id = data.get("experiment_id", "unknown")
        print(f"🔍 Analyzing {exp_id}...")
        
        # Check for timeline data
        raw_metrics = data.get("raw_metrics", {})
        timeline = raw_metrics.get("timeline", [])
        
        if not timeline:
            print(f"  ⚠️  No timeline data")
            issues.append(f"{exp_id}: Missing timeline")
        else:
            print(f"  ✅ Timeline: {len(timeline)} data points")
            
            # Check CPU values
            cpu_values = [p.get("cpu", 0) for p in timeline]
            cpu_peak = max(cpu_values)
            cpu_avg = sum(cpu_values) / len(cpu_values) if cpu_values else 0
            
            if cpu_peak == 0:
                print(f"  ⚠️  CPU always 0% (unrealistic)")
                issues.append(f"{exp_id}: CPU always 0%")
            else:
                print(f"  ✅ CPU: peak={cpu_peak:.1f}%, avg={cpu_avg:.1f}%")
            
            # Check memory values
            mem_values = [p.get("memory", 0) for p in timeline]
            mem_peak = max(mem_values)
            mem_avg = sum(mem_values) / len(mem_values) if mem_values else 0
            print(f"  ✅ Memory: peak={mem_peak:.1f}%, avg={mem_avg:.1f}%")
            
            # Check error counts
            error_counts = [p.get("error_count", 0) for p in timeline]
            total_errors = max(error_counts)
            print(f"  ✅ Errors: {total_errors}")
        
        # Check Grafana URL
        grafana_url = data.get("grafana_url")
        if grafana_url:
            print(f"  ✅ Grafana URL: {grafana_url}")
        else:
            print(f"  ⚠️  No Grafana URL")
            issues.append(f"{exp_id}: Missing Grafana URL")
        
        print()
    
    # Summary
    print("=" * 60)
    print(f"📈 Summary: {len(result_files)} experiments analyzed")
    if issues:
        print(f"⚠️  Found {len(issues)} issues:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ All experiments have good data quality!")
    print("=" * 60)

if __name__ == "__main__":
    analyze_experiment_results()
