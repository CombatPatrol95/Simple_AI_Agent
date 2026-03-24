"""
Scripting Agent — automation script generation and shell execution.
"""

from google.adk.agents import Agent

from agents.prompts import SCRIPTING_INSTRUCTION
from agents.tools.scripting_tools import generate_script, run_shell_command


scripting_agent = Agent(
    name="scripting_agent",
    model="gemini-2.0-flash",
    instruction=SCRIPTING_INSTRUCTION,
    description=(
        "Automation scripting specialist. Generates bash and Python scripts "
        "for DevOps tasks and can execute shell commands. Produces scripts "
        "with proper error handling, logging, and best practices."
    ),
    tools=[generate_script, run_shell_command],
)
