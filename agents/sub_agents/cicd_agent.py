"""
CI/CD Agent — generates and manages CI/CD pipeline configurations.
"""

from google.adk.agents import Agent

from ..prompts import CICD_INSTRUCTION
from ..tools.cicd_tools import (
    generate_github_actions,
    generate_gitlab_ci,
    list_workflows,
)


cicd_agent = Agent(
    name="cicd_agent",
    model="gemini-2.0-flash",
    instruction=CICD_INSTRUCTION,
    description=(
        "CI/CD pipeline specialist. Generates GitHub Actions and GitLab CI "
        "workflow configurations. Can also discover existing CI/CD files "
        "in a repository."
    ),
    tools=[generate_github_actions, generate_gitlab_ci, list_workflows],
)
