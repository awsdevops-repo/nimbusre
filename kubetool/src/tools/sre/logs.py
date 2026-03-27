import subprocess
import shlex
from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from src.tools.kubeconfig_utils import resolve_kubeconfig_path


ALLOWED_LOG_OPERATIONS = {
    "pod_logs",          # Get logs from a specific pod
    "pod_logs_follow",   # Stream logs from pod
    "search_logs",       # Search logs for patterns
    "log_stats",         # Log count and size stats
    "previous_logs",     # Get previous container logs (crashes)
    "logs_by_label",     # Get logs from pods matching labels
    "logs_by_node",      # Get logs from all pods on a node
    "failing_pods_logs", # Get logs from failing/error pods
}

DENY_KEYWORDS = {"rm", "delete", "truncate", "clear"}


class LogsInput(BaseModel):
    operation: Literal[
        "pod_logs", "pod_logs_follow", "search_logs", "log_stats",
        "previous_logs", "logs_by_label", "logs_by_node", "failing_pods_logs"
    ] = Field(..., description="Log operation to perform")
    namespace: Optional[str] = Field("default", description="Kubernetes namespace")
    pod_name: Optional[str] = Field(None, description="Pod name to query")
    container: Optional[str] = Field(None, description="Container name in pod")
    search_pattern: Optional[str] = Field(None, description="Regex pattern to search for")
    label_selector: Optional[str] = Field(None, description="Label selector for pods")
    node_name: Optional[str] = Field(None, description="Node to get logs from")
    lines: int = Field(100, description="Number of log lines to return")
    since: Optional[str] = Field(None, description="Show logs after timestamp (e.g., '10m', '1h')")
    kubeconfig: Optional[str] = Field(None, description="Path to kubeconfig file")


@tool("aggregate_logs", args_schema=LogsInput)
def logs_tool(
    operation: str,
    namespace: str = "default",
    pod_name: Optional[str] = None,
    container: Optional[str] = None,
    search_pattern: Optional[str] = None,
    label_selector: Optional[str] = None,
    node_name: Optional[str] = None,
    lines: int = 100,
    since: Optional[str] = None,
    kubeconfig: Optional[str] = None,
):
    """
    Aggregate and search logs from Kubernetes pods.
    
    Operations and required parameters:
    - pod_logs: Requires pod_name. Get logs from a specific pod
    - pod_logs_follow: Requires pod_name. Stream logs from a pod in real-time
    - previous_logs: Requires pod_name. Get logs from crashed container
    - logs_by_label: Requires label_selector. Get logs from pods matching labels
    - logs_by_node: Requires node_name. Get logs from all pods on a node
    - search_logs: Requires pod_name and search_pattern. Search logs for patterns
    - log_stats: Requires pod_name. Get log statistics (line count, size)
    - failing_pods_logs: Get logs from pods with failing status (Error, CrashLoopBackOff, etc.)
    
    Optional parameters:
    - namespace: Kubernetes namespace (default: 'default')
    - container: Container name in pod (if pod has multiple containers)
    - lines: Number of log lines to return (default: 100)
    - since: Show logs after timestamp (e.g., '10m', '1h')
    - kubeconfig: Path to kubeconfig file (uses default if not provided)
    """

    # Validate operation
    if operation not in ALLOWED_LOG_OPERATIONS:
        return f"Operation not allowed: {operation}"

    # Validate required parameters for each operation
    if operation == "pod_logs" and not pod_name:
        return f"pod_logs operation requires 'pod_name' parameter"
    if operation == "pod_logs_follow" and not pod_name:
        return f"pod_logs_follow operation requires 'pod_name' parameter"
    if operation == "previous_logs" and not pod_name:
        return f"previous_logs operation requires 'pod_name' parameter"
    if operation == "logs_by_label" and not label_selector:
        return f"logs_by_label operation requires 'label_selector' parameter"
    if operation == "logs_by_node" and not node_name:
        return f"logs_by_node operation requires 'node_name' parameter"
    if operation == "search_logs" and (not pod_name or not search_pattern):
        return f"search_logs operation requires both 'pod_name' and 'search_pattern' parameters"
    if operation == "log_stats" and not pod_name:
        return f"log_stats operation requires 'pod_name' parameter"

    # Validate patterns
    if search_pattern and any(keyword in search_pattern for keyword in DENY_KEYWORDS):
        return "Destructive keywords not allowed in search patterns"

    # Always use workspace kubeconfig first; ignore user-provided paths for safety
    kubeconfig = resolve_kubeconfig_path(user_path=kubeconfig, ignore_user_path=True)
    if not kubeconfig:
        return "No valid kubeconfig found. Please ensure kubectl is configured."

    # Build kubectl command
    cmd = _build_kubectl_cmd(
        operation, namespace, pod_name, container, search_pattern,
        label_selector, node_name, lines, since, kubeconfig
    )

    if not cmd:
        return f"Failed to build kubectl command for operation: {operation}"

    try:
        result = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=60,
        )
        return result

    except subprocess.CalledProcessError as e:
        return f"kubectl logs failed:\n{e.output}"
    except FileNotFoundError:
        return "kubectl not found. Please install kubectl."
    except Exception as e:
        return f"Error retrieving logs: {str(e)}"


def _build_kubectl_cmd(
    operation: str,
    namespace: str,
    pod_name: Optional[str],
    container: Optional[str],
    search_pattern: Optional[str],
    label_selector: Optional[str],
    node_name: Optional[str],
    lines: int,
    since: Optional[str],
    kubeconfig: Optional[str],
) -> list:
    """Build kubectl command for log retrieval."""

    base_cmd = ["kubectl", "logs"]

    # Add kubeconfig if provided
    if kubeconfig:
        base_cmd.extend(["--kubeconfig", kubeconfig])

    # Add namespace
    base_cmd.extend(["-n", namespace])

    if operation == "pod_logs":
        if not pod_name:
            return None  # pod_logs requires a pod name; use logs_by_label for multiple pods
        base_cmd.append(pod_name)
        if container:
            base_cmd.extend(["-c", container])
        base_cmd.extend(["--tail", str(lines)])
        if since:
            base_cmd.extend(["--since", since])
        return base_cmd

    elif operation == "pod_logs_follow":
        if not pod_name:
            return None
        base_cmd.extend(["-f", pod_name])
        if container:
            base_cmd.extend(["-c", container])
        return base_cmd

    elif operation == "previous_logs":
        if not pod_name:
            return None
        base_cmd.extend(["-p", pod_name])
        if container:
            base_cmd.extend(["-c", container])
        return base_cmd

    elif operation == "logs_by_label":
        if not label_selector:
            return None
        base_cmd.extend(["-l", label_selector, "--tail", str(lines)])
        if since:
            base_cmd.extend(["--since", since])
        return base_cmd

    elif operation == "logs_by_node":
        if not node_name:
            return None
        # Get all pods on node and stream logs
        return [
            "bash", "-c",
            f'kubectl get pods -n {namespace} --field-selector spec.nodeName={node_name} '
            f'-o jsonpath="{{.items[*].metadata.name}}" | '
            f'xargs -I {{}} kubectl logs -n {namespace} {{}} --tail={lines}'
        ]

    elif operation == "search_logs":
        if not pod_name or not search_pattern:
            return None
        kubeconfig_flag = f"--kubeconfig {shlex.quote(kubeconfig)} " if kubeconfig else ""
        container_flag = f"-c {shlex.quote(container)} " if container else ""
        return [
            "bash", "-c",
            f"kubectl logs {kubeconfig_flag}-n {shlex.quote(namespace)} "
            f"{shlex.quote(pod_name)} {container_flag}--tail={lines} | "
            f"grep -E -- {shlex.quote(search_pattern)}"
        ]

    elif operation == "log_stats":
        if not pod_name:
            return None
        kubeconfig_flag = f"--kubeconfig {shlex.quote(kubeconfig)} " if kubeconfig else ""
        container_flag = f"-c {shlex.quote(container)} " if container else ""
        # Get line and byte counts from recent log tail
        return [
            "bash", "-c",
            f"kubectl logs {kubeconfig_flag}-n {shlex.quote(namespace)} {shlex.quote(pod_name)} "
            f"{container_flag}--tail={lines} | wc -l && "
            f"kubectl logs {kubeconfig_flag}-n {shlex.quote(namespace)} {shlex.quote(pod_name)} "
            f"{container_flag}--tail={lines} | wc -c"
        ]

    elif operation == "failing_pods_logs":
        # Find failing pods and get their logs
        kubeconfig_flag = f"--kubeconfig {kubeconfig}" if kubeconfig else ""
        return [
            "bash", "-c",
            f'kubectl get pods -n {namespace} {kubeconfig_flag} '
            f'--field-selector=status.phase!=Running,status.phase!=Succeeded '
            f'-o jsonpath="{{.items[*].metadata.name}}" | '
            f'xargs -I {{}} kubectl logs -n {namespace} {kubeconfig_flag} {{}} --tail={lines} || '
            f'kubectl get pods -n {namespace} {kubeconfig_flag} '
            f'--field-selector=status.phase=Failed '
            f'-o jsonpath="{{.items[*].metadata.name}}" | '
            f'xargs -I {{}} kubectl logs -n {namespace} {kubeconfig_flag} {{}} --previous --tail={lines}'
        ]

    return None
