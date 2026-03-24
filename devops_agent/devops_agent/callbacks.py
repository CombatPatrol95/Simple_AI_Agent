"""
ADK callbacks for the DevOps agent system.
These hook into agent lifecycle events to manage state,
enforce safety checks, and maintain audit trails.
"""

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from .shared_state import (
    append_execution_log,
    REQUIRES_CONFIRMATION,
)


# ─── Dangerous command patterns that require user confirmation ────────────────

DANGEROUS_PATTERNS = [
    "delete", "destroy", "terminate", "remove",
    "drop", "purge", "force", "rm -rf",
    "scale --replicas=0", "kubectl delete",
]


def _is_dangerous(command: str) -> bool:
    """Check if a command contains dangerous patterns."""
    command_lower = command.lower()
    return any(pattern in command_lower for pattern in DANGEROUS_PATTERNS)


# ─── Agent Lifecycle Callbacks ────────────────────────────────────────────────

def before_agent_callback(callback_context: CallbackContext):
    """
    Runs before each agent invocation.
    - Logs the agent invocation to the execution log.
    - Injects common context from session state.
    """
    agent_name = callback_context.agent_name
    append_execution_log(
        callback_context.state,
        agent_name=agent_name,
        action="agent_started",
        result="pending",
    )
    # Return None to let the agent proceed normally
    return None


def after_agent_callback(callback_context: CallbackContext):
    """
    Runs after each agent completes.
    - Updates the execution log with completion status.
    """
    agent_name = callback_context.agent_name
    append_execution_log(
        callback_context.state,
        agent_name=agent_name,
        action="agent_completed",
        result="success",
    )
    return None


# ─── Tool Execution Callbacks ─────────────────────────────────────────────────

def before_tool_callback(
    tool_context: ToolContext, tool_name: str, tool_args: dict
):
    """
    Runs before each tool execution.
    - Validates dangerous operations and flags them for confirmation.
    - Returns a mock response to block execution if confirmation is needed.
    """
    # Check for dangerous commands in any string argument
    for arg_name, arg_value in tool_args.items():
        if isinstance(arg_value, str) and _is_dangerous(arg_value):
            # Flag in state for the UI / user to see
            tool_context.state[REQUIRES_CONFIRMATION] = {
                "tool": tool_name,
                "args": tool_args,
                "reason": f"Potentially destructive operation detected in '{arg_name}': {arg_value}",
            }
            # Block the tool by returning content directly
            return {
                "status": "blocked",
                "message": (
                    f"⚠️ This operation requires confirmation. "
                    f"The command contains a potentially destructive pattern. "
                    f"Tool: {tool_name}, Argument '{arg_name}': {arg_value}. "
                    f"Please confirm to proceed."
                ),
            }

    return None  # Allow tool execution to proceed


def after_tool_callback(
    tool_context: ToolContext, tool_name: str, tool_args: dict, tool_response
):
    """
    Runs after each tool execution.
    - Captures tool results into the execution log.
    - Stores results in session state for cross-agent access.
    """
    # Log the tool execution
    result_summary = str(tool_response)[:200] if tool_response else "no output"
    append_execution_log(
        tool_context.state,
        agent_name=tool_context.agent_name,
        action=f"tool:{tool_name}",
        result=result_summary,
    )

    return None  # Return None to use the original tool response
