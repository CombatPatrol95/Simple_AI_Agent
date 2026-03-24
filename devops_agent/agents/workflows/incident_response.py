"""
Incident Response Workflow — a SequentialAgent that orchestrates
multi-step incident investigation and resolution.

Steps:
1. MonitoringAgent: Investigate the alert, query metrics, check logs
2. CloudInfraAgent: Identify root cause in infrastructure
3. ScriptingAgent: Propose and generate a fix script

Note: We create dedicated agent instances for this workflow because
ADK enforces that each agent can only have one parent.
"""

from google.adk.agents import Agent, SequentialAgent

from ..prompts import (
    MONITORING_INSTRUCTION,
    CLOUD_INFRA_INSTRUCTION,
    SCRIPTING_INSTRUCTION,
)
from ..tools.monitoring_tools import query_metrics, check_alerts, get_service_logs
from ..tools.cloud_tools import run_aws_cli, run_gcp_cli, run_azure_cli
from ..tools.scripting_tools import generate_script, run_shell_command


# Workflow-specific agent instances (separate from the ones used by the coordinator)
_wf_monitoring = Agent(
    name="wf_monitoring_agent",
    model="gemini-2.0-flash",
    instruction=MONITORING_INSTRUCTION + "\nYou are part of an incident response workflow. Focus on investigating the alert and gathering relevant metrics and logs.",
    description="Monitoring agent for incident investigation step.",
    tools=[query_metrics, check_alerts, get_service_logs],
)

_wf_cloud_infra = Agent(
    name="wf_cloud_infra_agent",
    model="gemini-2.0-flash",
    instruction=CLOUD_INFRA_INSTRUCTION + "\nYou are part of an incident response workflow. Based on the monitoring findings in the session state, investigate the cloud infrastructure for root cause.",
    description="Cloud infra agent for incident root cause analysis.",
    tools=[run_aws_cli, run_gcp_cli, run_azure_cli],
)

_wf_scripting = Agent(
    name="wf_scripting_agent",
    model="gemini-2.0-flash",
    instruction=SCRIPTING_INSTRUCTION + "\nYou are part of an incident response workflow. Based on the root cause identified, generate a remediation script.",
    description="Scripting agent for incident remediation.",
    tools=[generate_script, run_shell_command],
)


incident_response_workflow = SequentialAgent(
    name="incident_response_workflow",
    description=(
        "Incident response workflow. Use this when investigating an alert or "
        "outage. Sequentially: (1) Monitoring Agent investigates the alert and "
        "gathers metrics/logs, (2) Cloud Infra Agent checks infrastructure for "
        "root cause, (3) Scripting Agent proposes and generates a remediation script."
    ),
    sub_agents=[_wf_monitoring, _wf_cloud_infra, _wf_scripting],
)
