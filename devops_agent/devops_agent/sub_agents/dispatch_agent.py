"""
Dispatch Agent — decomposes complex user requests into ordered subtasks.
"""

from google.adk.agents import Agent

from ..prompts import DISPATCH_INSTRUCTION


dispatch_agent = Agent(
    name="dispatch_agent",
    model="gemini-2.0-flash",
    instruction=DISPATCH_INSTRUCTION,
    description=(
        "Task decomposition specialist. Breaks down complex, multi-domain DevOps "
        "requests into discrete subtasks, each mapped to a specific sub-agent. "
        "Use this agent when the user request spans multiple DevOps domains."
    ),
    # No tools — this agent uses pure LLM reasoning to plan
)
