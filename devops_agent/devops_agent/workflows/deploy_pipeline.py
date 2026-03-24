"""
Deploy Pipeline Workflow — a combination of ParallelAgent and SequentialAgent
for orchestrating deployment operations.

Flow:
1. (Parallel) CICDAgent validates pipeline + KubernetesAgent checks cluster readiness
2. (Sequential) After parallel checks pass, proceed with deployment steps

Note: We create dedicated agent instances for this workflow because
ADK enforces that each agent can only have one parent.
"""

from google.adk.agents import Agent, ParallelAgent, SequentialAgent

from ..prompts import CICD_INSTRUCTION, KUBERNETES_INSTRUCTION
from ..tools.cicd_tools import generate_github_actions, generate_gitlab_ci, list_workflows
from ..tools.kubernetes_tools import list_pods, scale_deployment, get_pod_logs, apply_manifest


# Workflow-specific agent instances
_wf_cicd = Agent(
    name="wf_cicd_agent",
    model="gemini-2.0-flash",
    instruction=CICD_INSTRUCTION + "\nYou are part of a deployment workflow. Validate the CI/CD pipeline configuration and ensure it is ready for deployment.",
    description="CI/CD agent for deployment pipeline validation.",
    tools=[generate_github_actions, generate_gitlab_ci, list_workflows],
)

_wf_kubernetes = Agent(
    name="wf_kubernetes_agent",
    model="gemini-2.0-flash",
    instruction=KUBERNETES_INSTRUCTION + "\nYou are part of a deployment workflow. Check cluster readiness and ensure the target namespace and resources are prepared for deployment.",
    description="Kubernetes agent for deployment readiness checks.",
    tools=[list_pods, scale_deployment, get_pod_logs, apply_manifest],
)

# Step 1: Run CI/CD validation and K8s readiness checks in parallel
parallel_checks = ParallelAgent(
    name="deploy_parallel_checks",
    description=(
        "Runs CI/CD pipeline validation and Kubernetes cluster readiness "
        "checks in parallel to reduce deployment preparation time."
    ),
    sub_agents=[_wf_cicd, _wf_kubernetes],
)

# Step 2: Overall deployment workflow (checks first, then sequential deploy)
deploy_pipeline_workflow = SequentialAgent(
    name="deploy_pipeline_workflow",
    description=(
        "Deployment pipeline workflow. Use this for coordinated deployments. "
        "First runs CI/CD validation and K8s readiness checks in parallel, "
        "then proceeds with the sequential deployment steps."
    ),
    sub_agents=[parallel_checks],
)
