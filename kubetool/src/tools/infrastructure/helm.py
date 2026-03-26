import os
import tempfile
import subprocess
import json
from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool


# Keep this tight. Expand only as needed.
ALLOWED_OPERATIONS = {
    "install",      # Install a new chart
    "upgrade",      # Upgrade existing release
    "uninstall",    # Remove release
    "list",         # List releases
    "status",       # Check release status
    "get_values",   # Get release values
    "rollback",     # Rollback to previous version
    "search",       # Search for charts
    "get_notes",    # Get release notes/status notes
    "repo_add",     # Add helm repository
    "repo_list",    # List helm repositories
    "repo_update",  # Update helm repositories
}

DENY_FLAGS = {"--tiller-namespace", "--tiller-host"}  # Legacy flags
PROTECTED_NAMESPACES = {"kube-system", "kube-public", "kube-node-lease"}


class HelmInput(BaseModel):
    operation: Literal[
        "install", "upgrade", "uninstall", "list", "status", 
        "get_values", "rollback", "search", "get_notes",
        "repo_add", "repo_list", "repo_update"
    ] = Field(..., description="Helm operation to perform")
    release_name: Optional[str] = Field(None, description="Release name (required for install/upgrade/uninstall/status/get_values/rollback)")
    chart: Optional[str] = Field(None, description="Chart name/repo (required for install/upgrade/search)")
    repo_name: Optional[str] = Field(None, description="Repository name (required for repo_add)")
    repo_url: Optional[str] = Field(None, description="Repository URL (required for repo_add)")
    namespace: Optional[str] = Field(None, description="Kubernetes namespace (defaults to 'default')")
    version: Optional[str] = Field(None, description="Chart/release version")
    values: Optional[dict] = Field(default_factory=dict, description="Helm values to override")
    kubeconfig: Optional[str] = Field(None, description="Path to kubeconfig file")
    wait: bool = Field(default=True, description="Wait for resources to be ready")
    timeout: Optional[str] = Field(None, description="Timeout for operations (e.g., '5m')")


@tool("helm_deploy", args_schema=HelmInput)
def helm_tool(
    operation: str,
    release_name: Optional[str] = None,
    chart: Optional[str] = None,
    repo_name: Optional[str] = None,
    repo_url: Optional[str] = None,
    namespace: Optional[str] = None,
    version: Optional[str] = None,
    values: Optional[dict] = None,
    kubeconfig: Optional[str] = None,
    wait: bool = True,
    timeout: Optional[str] = None,
):
    """
    Deploy and manage Kubernetes applications using Helm.
    Supports install, upgrade, uninstall, list, status, rollback, and search operations.
    """

    if values is None:
        values = {}

    # Validate operation
    if operation not in ALLOWED_OPERATIONS:
        return f"Operation not allowed: {operation}"

    # Set namespace
    if not namespace:
        namespace = "default"

    # Protect system namespaces
    if namespace in PROTECTED_NAMESPACES and operation in {"install", "upgrade", "uninstall"}:
        return f"Cannot deploy to protected namespace: {namespace}. Use a user namespace."

    # Always use workspace kubeconfig - ignore LLM provided paths
    workspace_config = "/Users/amar.mani/source/ollama/kubetool/docker-desktop-config.yaml"
    if os.path.exists(workspace_config):
        kubeconfig = workspace_config
    else:
        # Fallback to default locations
        possible_configs = [
            os.path.expanduser("~/.kube/config"),
            "/etc/kubernetes/admin.conf"
        ]
        
        kubeconfig = None
        for config_path in possible_configs:
            if os.path.exists(config_path):
                kubeconfig = config_path
                break
        
        if not kubeconfig:
            return "No valid kubeconfig found. Please ensure kubectl is configured."

    # Build command based on operation
    cmd = _build_helm_command(operation, release_name, chart, repo_name, repo_url, namespace, version, values, wait, timeout)

    if not cmd:
        return f"Invalid parameters for operation: {operation}"

    try:
        # Set environment for kubeconfig
        env = {**os.environ, "KUBECONFIG": kubeconfig}
        
        # Completely disable all Docker credential mechanisms for macOS
        env["DOCKER_CONFIG"] = "/tmp/helm-docker-config"
        # Remove all Docker credential environment variables
        for key in list(env.keys()):
            if "DOCKER_CREDENTIAL" in key or "DOCKER_" in key:
                env.pop(key, None)
        
        # Create empty docker config to bypass all authentication
        os.makedirs("/tmp/helm-docker-config", exist_ok=True)
        docker_config = {}
        with open("/tmp/helm-docker-config/config.json", "w") as f:
            json.dump(docker_config, f)

        # Auto-add repository for install operations
        if operation == "install" and chart and "/" in chart:
            repo_name = chart.split("/")[0]
            _ensure_repo_exists(repo_name, kubeconfig)

        out = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30,  # Reduced from 300 to 30 seconds
            env=env,
        )
        return out

    except subprocess.CalledProcessError as e:
        return f"Helm command failed:\n{e.output}"
    except FileNotFoundError:
        return "helm not found. Please install Helm 3: https://helm.sh/docs/intro/install/"
    except Exception as e:
        return f"Error executing Helm command: {str(e)}"


def _build_helm_command(
    operation: str,
    release_name: Optional[str],
    chart: Optional[str],
    repo_name: Optional[str],
    repo_url: Optional[str],
    namespace: str,
    version: Optional[str],
    values: dict,
    wait: bool,
    timeout: Optional[str],
) -> list:
    """Build the Helm CLI command based on operation."""

    if operation == "repo_add":
        # Auto-provide URL for common repositories
        common_repos = {
            "bitnami": "https://charts.bitnami.com/bitnami",
            "stable": "https://charts.helm.sh/stable",
            "ingress-nginx": "https://kubernetes.github.io/ingress-nginx",
            "prometheus-community": "https://prometheus-community.github.io/helm-charts"
        }
        
        # If only repo_name provided, try to auto-complete URL
        if repo_name and not repo_url:
            if repo_name in common_repos:
                repo_url = common_repos[repo_name]
            else:
                return None  # Unknown repo, need URL
        
        # If neither provided, return error
        if not repo_name:
            return None
            
        return ["helm", "repo", "add", repo_name, repo_url]

    elif operation == "repo_list":
        return ["helm", "repo", "list", "-o", "json"]

    elif operation == "repo_update":
        return ["helm", "repo", "update"]

    elif operation == "list":
        return ["helm", "list", "-n", namespace, "-o", "json"]

    elif operation == "search":
        if not chart:
            return ["helm", "search", "repo", "--max-col-width=0"]
        return ["helm", "search", "repo", chart, "-o", "json"]

    elif operation == "status":
        if not release_name:
            # If no release specified, list all releases instead
            return ["helm", "list", "-n", namespace, "-o", "json"]
        return ["helm", "status", release_name, "-n", namespace, "-o", "json"]

    elif operation == "get_values":
        if not release_name:
            return None
        return ["helm", "get", "values", release_name, "-n", namespace, "-o", "json"]

    elif operation == "get_notes":
        if not release_name:
            return None
        return ["helm", "get", "notes", release_name, "-n", namespace]

    elif operation == "install":
        if not chart:
            return None
        # Generate release name if not provided
        if not release_name:
            # Extract chart name from repo/chart format
            chart_name = chart.split('/')[-1] if '/' in chart else chart
            release_name = chart_name.replace('.tgz', '').replace('.tar.gz', '')
        
        cmd = ["helm", "install", release_name, chart, "-n", namespace]
        if version:
            cmd.extend(["--version", version])
        cmd.extend(_add_values_flags(values))
        if wait:
            cmd.append("--wait")
        if timeout:
            cmd.extend(["--timeout", timeout])
        return cmd

    elif operation == "upgrade":
        if not release_name or not chart:
            return None
        cmd = ["helm", "upgrade", release_name, chart, "-n", namespace]
        if version:
            cmd.extend(["--version", version])
        cmd.extend(_add_values_flags(values))
        if wait:
            cmd.append("--wait")
        if timeout:
            cmd.extend(["--timeout", timeout])
        return cmd

    elif operation == "uninstall":
        if not release_name:
            return None
        cmd = ["helm", "uninstall", release_name, "-n", namespace]
        if wait:
            cmd.append("--wait")
        if timeout:
            cmd.extend(["--timeout", timeout])
        return cmd

    elif operation == "rollback":
        if not release_name or not version:
            return None
        cmd = ["helm", "rollback", release_name, version, "-n", namespace]
        if wait:
            cmd.append("--wait")
        if timeout:
            cmd.extend(["--timeout", timeout])
        return cmd

    return None


def _ensure_repo_exists(repo_name: str, kubeconfig: str) -> bool:
    """Ensure repository exists, add common ones if missing."""
    common_repos = {
        "bitnami": "https://charts.bitnami.com/bitnami",
        "stable": "https://charts.helm.sh/stable",
        "ingress-nginx": "https://kubernetes.github.io/ingress-nginx",
        "prometheus-community": "https://prometheus-community.github.io/helm-charts"
    }
    
    if repo_name in common_repos:
        try:
            env = {**os.environ, "KUBECONFIG": kubeconfig}
            # Add repo
            subprocess.run(
                ["helm", "repo", "add", repo_name, common_repos[repo_name]],
                env=env, check=True, capture_output=True
            )
            # Update repo
            subprocess.run(
                ["helm", "repo", "update"],
                env=env, check=True, capture_output=True
            )
            return True
        except:
            return False
    return False


def _add_values_flags(values: dict) -> list:
    """Convert values dict to Helm --set flags."""
    flags = []
    for key, val in values.items():
        # Escape string values properly
        if isinstance(val, str):
            flags.extend(["--set", f"{key}={val}"])
        elif isinstance(val, bool):
            flags.extend(["--set", f"{key}={str(val).lower()}"])
        elif isinstance(val, (int, float)):
            flags.extend(["--set", f"{key}={val}"])
    return flags
