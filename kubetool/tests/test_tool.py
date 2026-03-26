#!/usr/bin/env python3

import os
import subprocess
import tempfile

def kubectl_run(verb: str, resource: str, namespace: str = None, extra_args: list = None):
    if extra_args is None:
        extra_args = []
    
    # Read kubeconfig from file (in kubetool root directory)
    kubeconfig_path = os.path.join(os.path.dirname(__file__), "..", "docker-desktop-config.yaml")
    kubeconfig_path = os.path.abspath(kubeconfig_path)
    
    if not os.path.exists(kubeconfig_path):
        return f"Missing docker-desktop-config.yaml file at {kubeconfig_path}"
    
    # Basic safety checks
    ALLOWED_VERBS = {"get", "describe", "logs"}
    if verb not in ALLOWED_VERBS:
        return f"Verb not allowed: {verb}"
    
    try:
        cmd = ["kubectl", verb, resource]
        if namespace:
            cmd += ["-n", namespace]
        cmd += extra_args
        
        out = subprocess.check_output(
            cmd,
            env={**os.environ, "KUBECONFIG": kubeconfig_path},
            stderr=subprocess.STDOUT,
            text=True,
            timeout=60,
        )
        return out
    except subprocess.CalledProcessError as e:
        return f"kubectl failed:\n{e.output}"

def test_kubectl_tool():
    print("Testing kubectl tool...")
    
    # Test 1: Get pods
    print("\n1. Getting pods:")
    result = kubectl_run("get", "pods")
    print(result)
    
    # Test 2: Get pods in specific namespace
    print("\n2. Getting pods in kube-system:")
    result = kubectl_run("get", "pods", namespace="kube-system")
    print(result)
    
    # Test 3: Describe a service
    print("\n3. Describing services:")
    result = kubectl_run("describe", "svc")
    print(result)
    
    # Test 4: Get nodes
    print("\n4. Getting nodes:")
    result = kubectl_run("get", "nodes")
    print(result)
    
    # Test 5: Invalid verb (should be rejected)
    print("\n5. Testing invalid verb:")
    result = kubectl_run("apply", "deployment")
    print(result)

if __name__ == "__main__":
    test_kubectl_tool()