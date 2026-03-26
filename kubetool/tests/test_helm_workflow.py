#!/usr/bin/env python3

from src.workflows.basic import run_sre_session

# Test helm through basic workflow
print("=== Testing Helm through Basic Workflow ===")

result = run_sre_session(
    "List all helm releases in the default namespace and show their status",
    max_tools=3
)

print("\n=== Testing Helm Chart Installation ===")

result = run_sre_session(
    "Install nginx chart using helm in the test namespace",
    max_tools=3
)