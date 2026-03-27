"""Shared workflow wiring for tools and LLM initialization."""

from langchain_ollama import ChatOllama

from src.tools.sre.monitoring import monitoring_tool
from src.tools.sre.logs import logs_tool
from src.tools.sre.healing import healing_tool
from src.tools.sre.cost_analyzer import cost_analyzer_tool
from src.tools.infrastructure.kubectl import kubectl_tool
from src.tools.infrastructure.ansible import ansible_tool
from src.tools.infrastructure.helm import helm_tool


WORKFLOW_TOOLS = [
    kubectl_tool,
    ansible_tool,
    helm_tool,
    monitoring_tool,
    logs_tool,
    healing_tool,
    cost_analyzer_tool,
]


def get_llm_with_tools(model: str = "llama3.1:8b", temperature: float = 0):
    """Create a tool-bound LLM instance for workflow nodes."""
    return ChatOllama(model=model, temperature=temperature).bind_tools(WORKFLOW_TOOLS)


__all__ = [
    "WORKFLOW_TOOLS",
    "get_llm_with_tools",
    "kubectl_tool",
    "ansible_tool",
    "helm_tool",
    "monitoring_tool",
    "logs_tool",
    "healing_tool",
    "cost_analyzer_tool",
]
