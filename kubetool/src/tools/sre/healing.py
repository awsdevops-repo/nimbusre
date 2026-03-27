import subprocess
import json
import tempfile
from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool


ALLOWED_ACTIONS = {
    "restart_pod",         # Restart unhealthy pod
    "restart_deployment",  # Rollout restart deployment
    "scale_deployment",    # Scale up deployment replicas
    "drain_node",          # Gracefully drain node
    "cordon_node",         # Mark node unschedulable
    "uncordon_node",       # Mark node schedulable
    "create_policy",       # Create self-healing policy
    "check_health",        # Health check specific resource
    "evict_pod",           # Evict pod from node
}

PROTECTED_NAMESPACES = {"kube-system", "kube-public", "kube-node-lease"}
PROTECTED_DEPLOYMENTS = {"coredns", "metrics-server"}


class HealingInput(BaseModel):
    action: Literal[
        "restart_pod", "restart_deployment", "scale_deployment", "drain_node",
        "cordon_node", "uncordon_node", "create_policy", "check_health", "evict_pod"
    ] = Field(..., description="Self-healing action to perform")
    namespace: Optional[str] = Field("default", description="Kubernetes namespace")
    pod_name: Optional[str] = Field(None, description="Pod name")
    deployment_name: Optional[str] = Field(None, description="Deployment name")
    node_name: Optional[str] = Field(None, description="Node name")
    replicas: Optional[int] = Field(None, description="Number of replicas to scale to")
    health_check_type: Optional[str] = Field(None, description="Type of health check (liveness, readiness, startup)")
    policy_type: Optional[str] = Field(None, description="Policy type (restart_on_failure, scale_on_cpu_high, evict_on_pressure)")
    grace_period: Optional[int] = Field(None, description="Grace period in seconds")
    kubeconfig: Optional[str] = Field(None, description="Path to kubeconfig file")


@tool("self_healing", args_schema=HealingInput)
def healing_tool(
    action: str,
    namespace: str = "default",
    pod_name: Optional[str] = None,
    deployment_name: Optional[str] = None,
    node_name: Optional[str] = None,
    replicas: Optional[int] = None,
    health_check_type: Optional[str] = None,
    policy_type: Optional[str] = None,
    grace_period: Optional[int] = None,
    kubeconfig: Optional[str] = None,
):
    """
    Implement self-healing policies and automatic remediation.
    Restarts unhealthy pods, scales deployments, and manages node health.
    """

    # Validate action
    if action not in ALLOWED_ACTIONS:
        return f"Action not allowed: {action}"

    # Protect system namespaces from changes
    if namespace in PROTECTED_NAMESPACES and action in {"restart_pod", "scale_deployment"}:
        return f"Cannot execute action in protected namespace: {namespace}"

    # Protect critical deployments
    if deployment_name in PROTECTED_DEPLOYMENTS and action in {"restart_deployment"}:
        return f"Cannot restart critical deployment: {deployment_name}"

    # Build command
    cmd = _build_healing_command(
        action, namespace, pod_name, deployment_name, node_name,
        replicas, health_check_type, policy_type, grace_period, kubeconfig
    )

    if not cmd:
        return f"Invalid parameters for action: {action}"

    try:
        result = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=120,
        )
        return f"✅ Action completed: {action}\n{result}"

    except subprocess.CalledProcessError as e:
        return f"❌ Action failed:\n{e.output}"
    except FileNotFoundError:
        return "kubectl not found. Please install kubectl."
    except Exception as e:
        return f"Error executing healing action: {str(e)}"


def _build_healing_command(
    action: str,
    namespace: str,
    pod_name: Optional[str],
    deployment_name: Optional[str],
    node_name: Optional[str],
    replicas: Optional[int],
    health_check_type: Optional[str],
    policy_type: Optional[str],
    grace_period: Optional[int],
    kubeconfig: Optional[str],
) -> list:
    """Build kubectl command for healing action."""

    base_cmd = ["kubectl"]
    if kubeconfig:
        base_cmd.extend(["--kubeconfig", kubeconfig])

    if action == "restart_pod":
        if not pod_name:
            return None
        # Delete pod to trigger recreation
        return base_cmd + [
            "delete", "pod", pod_name,
            "-n", namespace,
            "--grace-period", str(grace_period or 30),
            "--wait=true"
        ]

    elif action == "restart_deployment":
        if not deployment_name:
            return None
        return base_cmd + [
            "rollout", "restart", f"deployment/{deployment_name}",
            "-n", namespace
        ]

    elif action == "scale_deployment":
        if not deployment_name or replicas is None:
            return None
        return base_cmd + [
            "scale", f"deployment/{deployment_name}",
            f"--replicas={replicas}",
            "-n", namespace
        ]

    elif action == "drain_node":
        if not node_name:
            return None
        return base_cmd + [
            "drain", node_name,
            "--ignore-daemonsets",
            "--delete-emptydir-data",
            f"--grace-period={grace_period or 30}"
        ]

    elif action == "cordon_node":
        if not node_name:
            return None
        return base_cmd + ["cordon", node_name]

    elif action == "uncordon_node":
        if not node_name:
            return None
        return base_cmd + ["uncordon", node_name]

    elif action == "evict_pod":
        if not pod_name:
            return None
        # Create eviction object
        eviction = {
            "apiVersion": "policy/v1",
            "kind": "Eviction",
            "metadata": {"name": pod_name, "namespace": namespace},
            "deleteOptions": {"gracePeriodSeconds": grace_period or 30}
        }
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(eviction, f)
            eviction_file = f.name
        
        return base_cmd + [
            "create", "-f", eviction_file,
            "-n", namespace
        ]

    elif action == "check_health":
        if not pod_name:
            return None
        # Check pod status and readiness
        return base_cmd + [
            "get", "pod", pod_name,
            "-n", namespace,
            "-o", "jsonpath={range .status.conditions[*]}{.type}={.status} {end}"
        ]

    elif action == "create_policy":
        if not policy_type:
            return None
        # Create self-healing policy via ConfigMap or webhook
        policy = _create_healing_policy(policy_type, namespace)
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(policy)
            policy_file = f.name
        
        return base_cmd + ["apply", "-f", policy_file]

    return None


def _create_healing_policy(policy_type: str, namespace: str) -> str:
    """Generate self-healing policy manifest."""

    if policy_type == "restart_on_failure":
        return f"""---
apiVersion: v1
kind: ConfigMap
metadata:
  name: healing-policy-restart
  namespace: {namespace}
data:
  policy: |
    If pod CrashLoopBackOff > 5 times:
      - Wait 2 minutes between restarts
      - After 10 failed restarts, alert on-call
      - Auto-rollback deployment to previous stable version
"""

    elif policy_type == "scale_on_cpu_high":
        return f"""---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: auto-scale-on-cpu
  namespace: {namespace}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: target-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
"""

    elif policy_type == "evict_on_pressure":
        return f"""---
apiVersion: v1
kind: ConfigMap
metadata:
  name: healing-policy-evict
  namespace: {namespace}
data:
  policy: |
    If node has MemoryPressure or DiskPressure:
      - Evict pods with lowest priority
      - Alert namespace owner
      - Recommend pod resource requests adjustment
"""

    return ""
