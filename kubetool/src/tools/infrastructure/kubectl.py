import os, tempfile, subprocess

from typing import Literal, Optional

from pydantic import BaseModel, Field

from langchain_core.tools import tool
 
# ✅ Keep this tight. Expand only as needed.

ALLOWED_VERBS = {"get", "describe", "logs"}

DENY_FLAGS = {"--kubeconfig"}  # we control kubeconfig ourselves
 
class KubectlInput(BaseModel):

    verb: Literal["get", "describe", "logs"] = Field(..., description="Allowed: get/describe/logs only")

    resource: str = Field(..., description="e.g. pods, svc, deployment, pod/my-pod")

    namespace: Optional[str] = Field(None, description="Namespace to use")

    extra_args: list[str] = Field(default_factory=list, description="Additional args (restricted)")
 
@tool("kubectl", args_schema=KubectlInput)

def kubectl_tool(verb: str, resource: str, namespace: Optional[str] = None, extra_args: Optional[list[str]] = None):

    """

    Run a restricted kubectl command using a kubeconfig from docker-desktop-config.yaml file.

    """
    
    # Try to read from docker-desktop-config.yaml file first, then fallback to env var
    kubeconfig_path = os.path.join(os.path.dirname(__file__), "../../../docker-desktop-config.yaml")
    
    if os.path.exists(kubeconfig_path):
        with open(kubeconfig_path, 'r') as f:
            kubeconfig_text = f.read()
    else:
        kubeconfig_text = os.environ.get("KUBECONFIG_TEXT")
        if not kubeconfig_text:
            return "Missing docker-desktop-config.yaml file or KUBECONFIG_TEXT env var."
 
    if extra_args is None:
        extra_args = []
    
    # Basic argument safety

    if verb not in ALLOWED_VERBS:

        return f"Verb not allowed: {verb}"

    if any(a in DENY_FLAGS for a in extra_args):

        return "Not allowed to pass --kubeconfig directly."

    if any(a in ("apply", "delete", "patch", "edit", "exec", "cp", "port-forward") for a in extra_args):

        return "Potentially destructive/interactive args are not allowed."
 
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:

        f.write(kubeconfig_text)

        temp_kubeconfig_path = f.name
 
    try:

        os.environ["PATH"] += ":/usr/bin"
        cmd = ["/usr/bin/kubectl", verb, resource]

        if namespace:

            cmd += ["-n", namespace]

        cmd += extra_args
 
        out = subprocess.check_output(

            cmd,

            env={**os.environ, "KUBECONFIG": temp_kubeconfig_path},

            stderr=subprocess.STDOUT,

            text=True,

            timeout=15,

        )

        return out

    except subprocess.CalledProcessError as e:

        return f"kubectl failed:\n{e.output}"

    finally:

        try:

            os.remove(temp_kubeconfig_path)

        except OSError:

            pass
