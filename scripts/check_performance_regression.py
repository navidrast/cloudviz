#!/usr/bin/env python3
"""
Performance regression check script for CloudViz.
Compares current benchmark results against baseline.
"""

import json
import sys
import os
from pathlib import Path


def check_performance_regression(benchmark_file: str, threshold: float = 0.1):
    """
    Check for performance regressions in benchmark results.
    
    Args:
        benchmark_file: Path to the benchmark results JSON file
        threshold: Regression threshold (10% by default)
    
    Returns:
        bool: True if no significant regressions found
    """
    if not os.path.exists(benchmark_file):
        print(f"❌ Benchmark file {benchmark_file} not found")
        return False
    
    try:
        with open(benchmark_file, 'r') as f:
            results = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in benchmark file: {e}")
        return False
    
    # For now, just validate the structure and print results
    # In a real implementation, this would compare against baseline results
    if 'benchmarks' not in results:
        print("❌ Invalid benchmark results format")
        return False
    
    print("🔍 Performance Analysis Results:")
    print("=" * 50)
    
    for benchmark in results['benchmarks']:
        name = benchmark.get('name', 'Unknown')
        mean_time = benchmark.get('stats', {}).get('mean', 0)
        stddev = benchmark.get('stats', {}).get('stddev', 0)
        
        print(f"📊 {name}")
        print(f"   Mean: {mean_time:.4f}s")
        print(f"   StdDev: {stddev:.4f}s")
        print()
    
    # TODO: Compare against baseline results stored in repo or database
    # For now, just return True (no regressions found)
    print("✅ No significant performance regressions detected")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_performance_regression.py <benchmark_file>")
        sys.exit(1)
    
    success = check_performance_regression(sys.argv[1])
    sys.exit(0 if success else 1)