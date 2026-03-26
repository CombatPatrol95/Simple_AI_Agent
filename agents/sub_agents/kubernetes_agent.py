"""
Kubernetes Agent — manages Kubernetes clusters and resources.
"""

from google.adk.agents import Agent

from agents.prompts import KUBERNETES_INSTRUCTION
from agents.tools.kubernetes_tools import (
    list_pods,
    scale_deployment,
    get_pod_logs,
    apply_manifest,
)


kubernetes_agent = Agent(
    name="kubernetes_agent",
    model="gemini-2.0-flash",
    instruction=KUBERNETES_INSTRUCTION,
    description=(
        "Kubernetes specialist. Manages cluster resources including pods, "
        "deployments, and services. Can list resources, scale deployments, "
        "retrieve logs, and apply YAML manifests."
    ),
    tools=[list_pods, scale_deployment, get_pod_logs, apply_manifest],
)
