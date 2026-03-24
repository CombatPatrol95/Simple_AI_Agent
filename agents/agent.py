"""
DevOps Coordinator — the root agent of the multi-agent DevOps system.

This is the main entry point that ADK discovers via __init__.py.
It coordinates all sub-agents and workflow agents, using callbacks
for state management, safety checks, and audit logging.
"""

from google.adk.agents import Agent

from .prompts import COORDINATOR_INSTRUCTION
from .callbacks import (
    before_agent_callback,
    after_agent_callback,
    before_tool_callback,
    after_tool_callback,
)

# Sub-agents
from .sub_agents.dispatch_agent import dispatch_agent
from .sub_agents.cloud_infra_agent import cloud_infra_agent
from .sub_agents.kubernetes_agent import kubernetes_agent
from .sub_agents.cicd_agent import cicd_agent
from .sub_agents.monitoring_agent import monitoring_agent
from .sub_agents.scripting_agent import scripting_agent

# Workflow agents
from .workflows.incident_response import incident_response_workflow
from .workflows.deploy_pipeline import deploy_pipeline_workflow


root_agent = Agent(
    name="devops_coordinator",
    model="gemini-2.0-flash",
    instruction=COORDINATOR_INSTRUCTION,
    description=(
        "DevOps Coordinator — the central orchestrator that delegates tasks to "
        "specialized sub-agents for cloud infrastructure, Kubernetes, CI/CD, "
        "monitoring, and scripting. Also orchestrates multi-step workflows for "
        "incident response and deployment pipelines."
    ),
    sub_agents=[
        dispatch_agent,
        cloud_infra_agent,
        kubernetes_agent,
        cicd_agent,
        monitoring_agent,
        scripting_agent,
        incident_response_workflow,
        deploy_pipeline_workflow,
    ],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)
