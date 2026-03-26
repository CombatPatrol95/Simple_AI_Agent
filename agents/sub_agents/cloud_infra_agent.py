"""
Cloud Infrastructure Agent — manages AWS, GCP, and Azure resources via CLI.
"""

from google.adk.agents import Agent

from agents.prompts import CLOUD_INFRA_INSTRUCTION
from agents.tools.cloud_tools import run_aws_cli, run_gcp_cli, run_azure_cli


cloud_infra_agent = Agent(
    name="cloud_infra_agent",
    model="gemini-2.0-flash",
    instruction=CLOUD_INFRA_INSTRUCTION,
    description=(
        "Cloud infrastructure specialist. Manages AWS, GCP, and Azure resources "
        "using their respective CLI tools. Handles provisioning, status checks, "
        "and resource management across all major cloud providers."
    ),
    tools=[run_aws_cli, run_gcp_cli, run_azure_cli],
)
