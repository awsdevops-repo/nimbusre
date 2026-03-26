#!/usr/bin/env python3

import os
import json
import tempfile
from helm_tool import helm_tool

def test_helm_tool():
    """Test the Helm deployment tool."""

    print("=" * 70)
    print("Testing Helm Deployment Tool")
    print("=" * 70)

    # Test 1: List releases
    print("\n🔍 Test 1: List Helm Releases")
    print("-" * 70)
    result = helm_tool(
        operation="list",
        namespace="default",
    )
    print(result)

    # Test 2: Search for charts
    print("\n🔍 Test 2: Search for Charts (nginx)")
    print("-" * 70)
    result = helm_tool(
        operation="search",
        chart="nginx",
    )
    print(result)

    # Test 3: Get status of a release
    print("\n🔍 Test 3: Get Status of Release (if exists)")
    print("-" * 70)
    result = helm_tool(
        operation="status",
        release_name="nginx",
        namespace="default",
    )
    print(result)

    # Test 4: Get values of a release
    print("\n🔍 Test 4: Get Values of Release (if exists)")
    print("-" * 70)
    result = helm_tool(
        operation="get_values",
        release_name="nginx",
        namespace="default",
    )
    print(result)

    # Test 5: Error handling - invalid operation
    print("\n⚠️  Test 5: Invalid Operation (should fail)")
    print("-" * 70)
    result = helm_tool(
        operation="invalid_op",
        release_name="test",
    )
    print(result)

    # Test 6: Error handling - protected namespace
    print("\n⚠️  Test 6: Protected Namespace (should fail)")
    print("-" * 70)
    result = helm_tool(
        operation="install",
        release_name="bad-install",
        chart="nginx",
        namespace="kube-system",
    )
    print(result)

    # Test 7: Error handling - missing required parameters
    print("\n⚠️  Test 7: Missing Required Parameters (should fail)")
    print("-" * 70)
    result = helm_tool(
        operation="install",
        release_name="incomplete",
        # Missing chart parameter
    )
    print(result)

    # Test 8: List releases in specific namespace
    print("\n🔍 Test 8: List Releases in kube-system")
    print("-" * 70)
    result = helm_tool(
        operation="list",
        namespace="kube-system",
    )
    print(result)

    print("\n" + "=" * 70)
    print("Tests completed!")
    print("=" * 70)


def example_install():
    """Example: Install a chart."""
    print("\n📦 Example: Install NGINX Ingress Controller")
    print("-" * 70)
    
    result = helm_tool(
        operation="install",
        release_name="nginx-ingress",
        chart="nginx-community/nginx-ingress",
        namespace="ingress-nginx",
        values={
            "replicaCount": "2",
            "serviceType": "LoadBalancer",
        },
        wait=True,
        timeout="10m",
    )
    print(result)


def example_upgrade():
    """Example: Upgrade a release."""
    print("\n🔄 Example: Upgrade Release")
    print("-" * 70)
    
    result = helm_tool(
        operation="upgrade",
        release_name="nginx-ingress",
        chart="nginx-community/nginx-ingress",
        namespace="ingress-nginx",
        values={
            "replicaCount": "3",
        },
        wait=True,
    )
    print(result)


def example_rollback():
    """Example: Rollback a release."""
    print("\n↩️  Example: Rollback Release")
    print("-" * 70)
    
    result = helm_tool(
        operation="rollback",
        release_name="nginx-ingress",
        version="1",  # Rollback to revision 1
        namespace="ingress-nginx",
        wait=True,
    )
    print(result)


if __name__ == "__main__":
    # Run tests
    test_helm_tool()
    
    # Uncomment to run examples (requires Helm setup)
    # example_install()
    # example_upgrade()
    # example_rollback()
