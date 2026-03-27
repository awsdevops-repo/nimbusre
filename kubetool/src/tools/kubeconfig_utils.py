"""Shared kubeconfig resolution helpers for tools."""

from pathlib import Path
import os
from typing import Optional


_WORKSPACE_KUBECONFIG = Path(__file__).resolve().parents[2] / "docker-desktop-config.yaml"
_DEFAULT_KUBECONFIGS = [
    Path.home() / ".kube" / "config",
    Path("/etc/kubernetes/admin.conf"),
]


def resolve_kubeconfig_path(
    user_path: Optional[str] = None,
    ignore_user_path: bool = True,
) -> Optional[str]:
    """Return kubeconfig path using workspace-first resolution and safe fallbacks."""
    if _WORKSPACE_KUBECONFIG.exists():
        return str(_WORKSPACE_KUBECONFIG)

    if not ignore_user_path and user_path and os.path.exists(user_path):
        return user_path

    for config_path in _DEFAULT_KUBECONFIGS:
        if config_path.exists():
            return str(config_path)

    return None


def read_workspace_kubeconfig_or_env(env_var: str = "KUBECONFIG_TEXT") -> Optional[str]:
    """Read workspace kubeconfig content, or fallback to env var content."""
    if _WORKSPACE_KUBECONFIG.exists():
        return _WORKSPACE_KUBECONFIG.read_text(encoding="utf-8")
    return os.environ.get(env_var)
