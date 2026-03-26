#!/usr/bin/env python3

from monitoring_tool import monitoring_tool
from logs_tool import logs_tool
from healing_tool import healing_tool
from cost_analyzer_tool import cost_analyzer_tool

def test_monitoring():
    """Test monitoring tool."""
    print("\n" + "="*70)
    print("Testing Monitoring Tool (Prometheus/Grafana)")
    print("="*70)
    
    tests = [
        ("Available metrics", dict(query_type="available_metrics")),
        ("CPU usage", dict(query_type="cpu_usage", namespace="default")),
        ("Memory usage", dict(query_type="memory_usage", namespace="default")),
        ("Pod restart count", dict(query_type="pod_restart_count", namespace="default")),
        ("Alert status", dict(query_type="alert_status")),
    ]
    
    for desc, params in tests:
        print(f"\n🔍 {desc}")
        result = monitoring_tool(**params)
        print(result[:200] + "..." if len(result) > 200 else result)


def test_logs():
    """Test logs tool."""
    print("\n" + "="*70)
    print("Testing Log Aggregation Tool")
    print("="*70)
    
    tests = [
        ("Get pod logs", dict(operation="pod_logs", namespace="default", pod_name="example-pod", lines=50)),
        ("Check health", dict(operation="check_health", namespace="default", pod_name="example-pod")),
        ("Invalid operation", dict(operation="invalid_op", namespace="default", pod_name="example-pod")),
    ]
    
    for desc, params in tests:
        print(f"\n📋 {desc}")
        result = logs_tool(**params)
        print(result[:200] + "..." if len(result) > 200 else result)


def test_healing():
    """Test healing tool."""
    print("\n" + "="*70)
    print("Testing Self-Healing Tool")
    print("="*70)
    
    tests = [
        ("Check pod health", dict(action="check_health", namespace="default", pod_name="example-pod")),
        ("Protected namespace check", dict(action="restart_pod", namespace="kube-system", pod_name="test", grace_period=30)),
        ("Scale deployment", dict(action="scale_deployment", namespace="default", deployment_name="myapp", replicas=3)),
        ("Cordon node", dict(action="cordon_node", node_name="node-1")),
    ]
    
    for desc, params in tests:
        print(f"\n🏥 {desc}")
        result = healing_tool(**params)
        print(result[:200] + "..." if len(result) > 200 else result)


def test_cost_analysis():
    """Test cost analyzer tool."""
    print("\n" + "="*70)
    print("Testing Cost Analysis Tool")
    print("="*70)
    
    tests = [
        ("Resource waste", dict(analysis_type="resource_waste")),
        ("Cost by namespace", dict(analysis_type="cost_by_namespace")),
        ("Unused PVCs", dict(analysis_type="unused_pvcs")),
        ("Node utilization", dict(analysis_type="node_utilization")),
        ("Optimization opportunities", dict(analysis_type="optimization_opportunities")),
        ("Cluster cost estimate", dict(analysis_type="cluster_cost", time_period="30d")),
    ]
    
    for desc, params in tests:
        print(f"\n💰 {desc}")
        result = cost_analyzer_tool(**params)
        print(result[:300] + "..." if len(result) > 300 else result)


if __name__ == "__main__":
    test_monitoring()
    test_logs()
    test_healing()
    test_cost_analysis()
    
    print("\n" + "="*70)
    print("All tests completed!")
    print("="*70)
