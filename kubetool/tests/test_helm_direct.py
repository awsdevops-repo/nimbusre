#!/usr/bin/env python3

from src.tools.infrastructure.helm import helm_tool

# Test 1: List releases
print("=== Test 1: List Helm releases ===")
result = helm_tool.invoke({
    "operation": "list",
    "namespace": "default"
})
print(result)

# Test 2: Search for charts
print("\n=== Test 2: Search for nginx chart ===")
result = helm_tool.invoke({
    "operation": "search",
    "chart": "nginx"
})
print(result)

# Test 3: Install a chart (dry-run)
print("\n=== Test 3: Install nginx chart (dry-run) ===")
result = helm_tool.invoke({
    "operation": "install",
    "release_name": "test-nginx",
    "chart": "bitnami/nginx",
    "namespace": "default",
    "values": {"service.type": "ClusterIP"}
})
print(result)